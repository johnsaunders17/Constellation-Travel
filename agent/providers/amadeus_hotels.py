# agent/providers/amadeus_hotels.py
import os
import requests
from datetime import datetime, timedelta

AMADEUS_BASE = "https://test.api.amadeus.com"
TOKEN_URL = f"{AMADEUS_BASE}/v1/security/oauth2/token"

_client_token = None
_token_expiry = None


def _auth():
    global _client_token, _token_expiry
    if _client_token and _token_expiry and datetime.utcnow() < _token_expiry:
        return _client_token

    key = os.getenv("AMADEUS_API_KEY")
    secret = os.getenv("AMADEUS_API_SECRET")
    if not key or not secret:
        raise RuntimeError("Missing AMADEUS_API_KEY or AMADEUS_API_SECRET")

    print("[INFO] Authenticating with Amadeus...")
    resp = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(key, secret),
        timeout=10,
    )
    resp.raise_for_status()
    payload = resp.json()
    _client_token = payload["access_token"]
    _token_expiry = datetime.utcnow() + timedelta(seconds=int(payload["expires_in"]) - 60)
    return _client_token


def _city_hotels(city, radius_km=30):
    """Try multiple fallbacks to fetch hotel IDs for a city."""
    token = _auth()
    attempts = [
        (radius_km, True, True),
        (20, True, True),
        (20, False, True),
        (20, False, False),  # last resort
    ]
    for rad, use_source, use_limit in attempts:
        params = {
            "cityCode": city,
            "radius": rad,
            "radiusUnit": "KM",
        }
        if use_source:
            params["hotelSource"] = "ALL"
        if use_limit:
            params["page[limit]"] = 50

        r = requests.get(
            f"{AMADEUS_BASE}/v1/reference-data/locations/hotels/by-city",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=10,
        )

        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                print(f"[Amadeus/Hotels] by-city SUCCESS city={city} r={rad} source={use_source} limit={use_limit} -> {len(data)} hotels")
                return [h.get("hotelId") for h in data if h.get("hotelId")]
        else:
            print(f"[Amadeus/Hotels] by-city {city} r={rad} (source={use_source},limit={use_limit}) -> {r.status_code}: {r.text}")

    return []


def get_amadeus_hotels(params):
    """Search hotels via Amadeus API given a set of params from config."""
    city_code = params.get("destination")
    check_in = params.get("startDate")
    nights = int(params.get("nights", 1))
    check_out = (datetime.strptime(check_in, "%Y-%m-%d") + timedelta(days=nights)).strftime("%Y-%m-%d")

    hotel_ids = _city_hotels(city_code, radius_km=int(params.get("radius", 30)))
    if not hotel_ids:
        print(f"[Amadeus/Hotels] No hotels found for city {city_code}")
        return []

    token = _auth()
    offers = []
    for hid in hotel_ids:
        r = requests.get(
            f"{AMADEUS_BASE}/v3/shopping/hotel-offers",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "hotelIds": hid,
                "adults": params.get("adults", 2),
                "checkInDate": check_in,
                "checkOutDate": check_out,
                "roomQuantity": 1,
                "currency": params.get("currency", "GBP"),
            },
            timeout=10,
        )
        if r.status_code != 200:
            print(f"[Amadeus/Hotels] offers {hid} -> {r.status_code}: {r.text}")
            continue

        data = r.json().get("data", [])
        for item in data:
            hotel = item.get("hotel", {}) or {}
            rating_raw = (
                hotel.get("rating")
                or hotel.get("stars")
                or hotel.get("category")
                or ""
            )

            stars = 0
            if isinstance(rating_raw, (int, float)):
                try:
                    stars = int(rating_raw)
                except Exception:
                    stars = 0
            elif isinstance(rating_raw, str):
                s = rating_raw.strip().upper()
                if s.isdigit():
                    stars = int(s)
                else:
                    if "FIVE" in s:
                        stars = 5
                    elif "FOUR" in s:
                        stars = 4
                    elif "THREE" in s:
                        stars = 3
                    elif "TWO" in s:
                        stars = 2
                    elif "ONE" in s:
                        stars = 1
                    else:
                        stars = 0

            for offer in item.get("offers", []):
                price_total = offer.get("price", {}).get("total")
                board = (
                    offer.get("boardType")
                    or (offer.get("mealPlan") or {}).get("code")
                    or (offer.get("mealPlan") or {}).get("type")
                    or "Unknown"
                )
                board = str(board).upper()

                offers.append({
                    "provider": "Amadeus Hotels",
                    "providerCode": "amadeus",
                    "name": hotel.get("name"),
                    "stars": stars,
                    "board": board,
                    "price": float(price_total) if price_total else None,
                    "checkIn": check_in,
                    "checkOut": check_out,
                    "raw": item,
                })

    return offers
