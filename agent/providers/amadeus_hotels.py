import os
import time
import json
import requests
from datetime import datetime, timedelta
from typing import List

AMADEUS_BASE = os.getenv("AMADEUS_BASE", "https://test.api.amadeus.com")
CLIENT_ID = os.getenv("AMADEUS_API_KEY")
CLIENT_SECRET = os.getenv("AMADEUS_API_SECRET")

_TOKEN = {"value": None, "exp": 0}

def _token() -> str:
    if _TOKEN["value"] and time.time() < _TOKEN["exp"] - 60:
        return _TOKEN["value"]
    if not (CLIENT_ID and CLIENT_SECRET):
        raise RuntimeError("Missing AMADEUS_API_KEY or AMADEUS_API_SECRET")
    resp = requests.post(
        f"{AMADEUS_BASE}/v1/security/oauth2/token",
        data={"grant_type": "client_credentials",
              "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    _TOKEN["value"] = data["access_token"]
    _TOKEN["exp"] = time.time() + int(data.get("expires_in", 1800))
    return _TOKEN["value"]

def _resolve_city_code(params: dict) -> str:
    """
    Accept multiple keys from different callers and normalise to a 3‑letter city code.
    Priority order matches your smoke tests and agent config.
    """
    candidates = [
        params.get("destinationCityCode"),
        params.get("cityCode"),
        params.get("destinationCity"),
        params.get("destinationIata"),
        params.get("destination"),           # can be IATA
        params.get("destinationAirport"),
    ]
    for c in candidates:
        if not c:
            continue
        s = str(c).strip().upper()
        # tolerate values like "ALC", " alc ", or "ALC-ES"
        if len(s) >= 3:
            s = s[:3]
        if s.isalpha() and len(s) == 3:
            return s
    return ""

def _city_hotels(city_code: str, radius_km: int = 30, limit: int = 50) -> List[str]:
    """
    GET /v1/reference-data/locations/hotels/by-city to fetch hotelIds.
    Retries with safer params if the sandbox rejects the request.
    """
    if not city_code:
        print("[Amadeus/Hotels] Missing city code; cannot query by-city.")
        return []

    headers = {"Authorization": f"Bearer {_token()}"}

    def call(city: str, rad: int, use_source: bool, use_limit: bool) -> requests.Response:
        q = {"cityCode": city, "radius": rad, "radiusUnit": "KM"}
        if use_source:
            q["hotelSource"] = "ALL"
        if use_limit:
            q["page[limit]"] = min(limit, 50)
        return requests.get(f"{AMADEUS_BASE}/v1/reference-data/locations/hotels/by-city",
                            headers=headers, params=q, timeout=20)

    tries = [
        (city_code, min(max(int(radius_km), 1), 30), True, True),
        (city_code, 20, True, True),
        (city_code, 20, False, True),
        (city_code, 20, False, False),
    ]

    for city, rad, use_source, use_limit in tries:
        r = call(city, rad, use_source, use_limit)
        if r.status_code == 401:
            headers["Authorization"] = f"Bearer {_token()}"
            r = call(city, rad, use_source, use_limit)

        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                print(f"[Amadeus/Hotels] by-city SUCCESS city={city} r={rad} source={use_source} limit={use_limit} -> {len(data)} hotels")
                return [h.get("hotelId") for h in data if h.get("hotelId")]
            # 200 but empty; continue to next try
        else:
            msg = r.text[:300] if hasattr(r, "text") else str(r.status_code)
            print(f"[Amadeus/Hotels] by-city {city} r={rad} (source={use_source},limit={use_limit}) -> {r.status_code}: {msg}")

    return []

def _compute_checkout(check_in: str, nights: int) -> str:
    y, m, d = map(int, check_in.split("-"))
    return (datetime(y, m, d) + timedelta(days=int(nights))).date().isoformat()

def get_amadeus_hotels(params: dict) -> list:
    """
    Search hotels using:
      1) v1 by-city to get hotelIds
      2) v3 shopping/hotel-offers to get priced offers (batched)
    Required: destinationCityCode (or destination=ALC), startDate, nights, adults
    """
    city_code = _resolve_city_code(params)
    check_in = params.get("startDate")
    nights = int(params.get("nights", 1))
    if not (city_code and check_in):
        print(f"[Amadeus/Hotels] Missing inputs city_code='{city_code}' startDate='{check_in}'")
        return []

    check_out = _compute_checkout(check_in, nights)
    adults = int(params.get("adults", 2))
    rooms = int(params.get("roomQuantity", 1))
    currency = (params.get("currency") or "GBP").upper()
    radius = int(params.get("radius", 30))

    hotel_ids = _city_hotels(city_code, radius_km=radius)
    if not hotel_ids:
        print(f"[Amadeus/Hotels] No hotelIds for {city_code}")
        return []

    # Batch request (one call) up to 30 hotelIds to avoid rate limits
    hotel_ids = hotel_ids[:30]
    headers = {"Authorization": f"Bearer {_token()}"}
    q = {
        "hotelIds": ",".join(hotel_ids),
        "adults": adults,
        "roomQuantity": rooms,
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "currency": currency,
        "bestRateOnly": "true",
        "paymentPolicy": "NONE",
        "view": "FULL",
        "includeClosed": "false",
        "cityCode": city_code,
    }
    r = requests.get(f"{AMADEUS_BASE}/v3/shopping/hotel-offers", headers=headers, params=q, timeout=30)
    if r.status_code == 401:
        headers["Authorization"] = f"Bearer {_token()}"
        r = requests.get(f"{AMADEUS_BASE}/v3/shopping/hotel-offers", headers=headers, params=q, timeout=30)
    r.raise_for_status()

    payload = r.json()
    data = payload.get("data", [])

    out = []
    for item in data:
        hotel = item.get("hotel", {}) or {}

        # Robust star rating extraction
        rating_raw = hotel.get("rating") or hotel.get("stars") or hotel.get("category") or ""
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
                if "FIVE" in s: stars = 5
                elif "FOUR" in s: stars = 4
                elif "THREE" in s: stars = 3
                elif "TWO" in s: stars = 2
                elif "ONE" in s: stars = 1
                else: stars = 0

        for offer in item.get("offers", []):
            price_total = offer.get("price", {}).get("total")
            board = (
                offer.get("boardType")
                or (offer.get("mealPlan") or {}).get("code")
                or (offer.get("mealPlan") or {}).get("type")
                or "Unknown"
            )
            board = str(board).upper()

            out.append({
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

    return out
