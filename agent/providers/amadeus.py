import os
import requests
from datetime import datetime, timedelta

def get_amadeus_access_token():
    print("[INFO] Authenticating with Amadeus...")
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("AMADEUS_API_KEY"),
        "client_secret": os.getenv("AMADEUS_API_SECRET")
    }

    res = requests.post(url, headers=headers, data=data)
    res.raise_for_status()
    return res.json()["access_token"]

def get_amadeus_hotels(params):
    token = get_amadeus_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    check_in = params["startDate"]
    check_out = (datetime.strptime(check_in, "%Y-%m-%d") + timedelta(days=params["nights"])).strftime("%Y-%m-%d")

    query = {
        "cityCode": "ALC",  # Alicante — closest valid Amadeus cityCode for Benidorm
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "adults": params["adults"],
        "roomQuantity": 1,
        "radius": 30,
        "radiusUnit": "KM",
        "bestRateOnly": "true",
        "view": "FULL",
        "currency": "GBP"
    }

    print("[INFO] Calling Amadeus hotel offers endpoint...")
    url = "https://test.api.amadeus.com/v2/shopping/hotel-offers"
    res = requests.get(url, headers=headers, params=query)
    res.raise_for_status()

    raw_data = res.json().get("data", [])
    results = []

    for item in raw_data:
        hotel = item.get("hotel", {})
        offer = item.get("offers", [{}])[0]

        results.append({
            "provider": "Amadeus",
            "name": hotel.get("name"),
            "stars": hotel.get("rating", 3),
            "rating": hotel.get("rating", 3),
            "board": offer.get("boardType", "Unknown"),
            "price": float(offer.get("price", {}).get("total", 0)),
            "link": hotel.get("contact", {}).get("uri", "")
        })

    return results
