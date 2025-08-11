import os
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

AMADEUS_BASE_URL = "https://test.api.amadeus.com"

def get_amadeus_access_token():
    client_id = os.getenv("AMADEUS_API_KEY")
    client_secret = os.getenv("AMADEUS_API_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("AMADEUS_API_KEY and AMADEUS_API_SECRET must be set")

    print("[INFO] Authenticating with Amadeus...")
    url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    try:
        res = requests.post(url, headers=headers, data=data)
        res.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"[Amadeus] Token request failed: {e}")
    return res.json()["access_token"]

def get_amadeus_hotels(params):
    token = get_amadeus_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    check_in = params["startDate"]
    check_out = (datetime.strptime(check_in, "%Y-%m-%d") + timedelta(days=params["nights"])).strftime("%Y-%m-%d")


       # Step 1: find hotels near the city
    list_url = f"{AMADEUS_BASE_URL}/v1/reference-data/locations/hotels/by-city"
    list_params = {
        "cityCode": params.get("destination", "ALC"),  # Alicante (nearest airport to Benidorm)
        "radius": 30,
        "radiusUnit": "KM"
    }
    try:
        list_res = requests.get(list_url, headers=headers, params=list_params)
        list_res.raise_for_status()
    except Exception:
        logger.exception("[Amadeus] Hotel list API call failed")
        return []

    hotels_data = list_res.json().get("data", [])
    hotel_ids = [h.get("hotelId") for h in hotels_data if h.get("hotelId")]
    if not hotel_ids:
        logger.info("[Amadeus] No hotels found for city")
        return []

    # Step 2: fetch offers for those hotelIds
    offers_url = f"{AMADEUS_BASE_URL}/v3/shopping/hotel-offers"
    offers_params = {
        "hotelIds": ",".join(hotel_ids[:20]),   # limit to first 20 IDs to keep URL manageable
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "adults": params["adults"],
        "roomQuantity": 1,
        "currency": "GBP"
    }
    try:
        offers_res = requests.get(offers_url, headers=headers, params=offers_params)
        offers_res.raise_for_status()
    except Exception:
        logger.exception("[Amadeus] Hotel offers API call failed")
        return []

    raw_data = offers_res.json().get("data", [])
    results = []
    for item in raw_data:
        hotel = item.get("hotel", {})
        offers = item.get("offers", [])
        for offer in offers:
            board = offer.get("boardType") or offer.get("description", {}).get("text", "Unknown")
            price_total = offer.get("price", {}).get("total")
            results.append({
                "provider": "Amadeus",
                "name": hotel.get("name"),
                "stars": hotel.get("rating", 3),
                "rating": hotel.get("rating", 3),
                "board": board,
                "price": float(price_total) if price_total else 0.0,
                "link": hotel.get("contact", {}).get("uri", "")
            })

    return results
  
