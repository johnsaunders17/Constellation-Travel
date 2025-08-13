import os
import time
import requests

AMADEUS_BASE = os.getenv("AMADEUS_BASE", "https://test.api.amadeus.com")
CLIENT_ID = os.getenv("AMADEUS_API_KEY")
CLIENT_SECRET = os.getenv("AMADEUS_API_SECRET")

_TOKEN = {"value": None, "exp": 0}

def _token():
    if _TOKEN["value"] and time.time() < _TOKEN["exp"] - 60:
        return _TOKEN["value"]
    r = requests.post(
        f"{AMADEUS_BASE}/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    _TOKEN["value"] = data["access_token"]
    _TOKEN["exp"] = time.time() + int(data.get("expires_in", 1800))
    return _TOKEN["value"]

def _city_hotels(city_code: str, radius_km: int = 30, limit: int = 50) -> list[str]:
    """
    GET /v1/reference-data/locations/hotels/by-city to fetch hotelIds.
    Retries with safer params if the sandbox rejects the request, and falls back to MAD.
    """
    headers = {"Authorization": f"Bearer {_token()}"}

    def call(city: str, rad: int, use_source: bool, use_limit: bool) -> requests.Response:
        q = {"cityCode": city.upper(), "radius": rad, "radiusUnit": "KM"}
        if use_source:
            q["hotelSource"] = "ALL"
        if use_limit:
            q["page[limit]"] = min(limit, 50)
        return requests.get(f"{AMADEUS_BASE}/v1/reference-data/locations/hotels/by-city",
                            headers=headers, params=q, timeout=20)

    # Try 1: as requested
    tries = [
        (city_code, min(max(int(radius_km), 1), 30), True, True),
        # Try 2: stricter radius (<=20), keep source/limit
        (city_code, 20, True, True),
        # Try 3: drop hotelSource (some sandboxes reject it)
        (city_code, 20, False, True),
        # Try 4: drop page[limit] as well
        (city_code, 20, False, False),
        # Try 5: fallback city known to work in sandbox
        ("MAD", 20, False, False),
    ]

    for city, rad, use_source, use_limit in tries:
        r = call(city, rad, use_source, use_limit)
        if r.status_code == 401:
            _TOKEN["value"] = None
            headers["Authorization"] = f"Bearer {_token()}"
            r = call(city, rad, use_source, use_limit)

        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return [h.get("hotelId") for h in data if h.get("hotelId")]
            # 200 but empty – keep falling through
        else:
            # Log the first 300 chars of error to help debugging
            try:
                msg = r.text[:300]
            except Exception:
                msg = str(r.status_code)
            print(f"[Amadeus/Hotels] by-city {city} r={rad} (source={use_source},limit={use_limit}) -> {r.status_code}: {msg}")

    return []

def get_amadeus_hotels(params: dict) -> list[dict]:
    """
    Search hotels using v1 by-city to get hotelIds, then v3 offers.
    Required: destinationCityCode (IATA city code like ALC), startDate, nights, adults
    Optional: roomQuantity, currency
    """
    if not (CLIENT_ID and CLIENT_SECRET):
        print("[Amadeus/Hotels] Missing credentials.")
        return []

    city_code = (params.get("destinationCityCode") or params.get("destination") or "ALC").upper()
    check_in = params.get("startDate")
    nights = int(params.get("nights", 4))
    if not check_in:
        print("[Amadeus/Hotels] Missing startDate; skipping.")
        return []
    from datetime import datetime, timedelta
    y, m, d = map(int, check_in.split("-"))
    check_out = (datetime(y, m, d) + timedelta(days=nights)).date().isoformat()

    adults = int(params.get("adults", 2))
    rooms = int(params.get("roomQuantity", 1))
    currency = (params.get("currency") or "GBP").upper()

    # Step 1: hotelIds
    hotel_ids = _city_hotels(city_code, radius_km=int(params.get("radius", 30)))
    if not hotel_ids:
        print(f"[Amadeus/Hotels] No hotelIds for {city_code}")
        return []
    # Be conservative on list length
    hotel_ids = hotel_ids[:30]

    # Step 2: offers
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
        _TOKEN["value"] = None
        headers["Authorization"] = f"Bearer {_token()}"
        r = requests.get(f"{AMADEUS_BASE}/v3/shopping/hotel-offers", headers=headers, params=q, timeout=30)
    r.raise_for_status()

    payload = r.json()
    data = payload.get("data", [])
        out = []
    for item in data:
        hotel = item.get("hotel", {}) or {}
        # --- Robust star rating extraction ---
        # Amadeus may return:
        # - hotel.rating: "3" or "THREE_STAR"
        # - hotel.category: "THREE_STAR" / "FOUR_STAR"
        # - hotel.stars: 3 (rare)
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
            # numeric string?
            if s.isdigit():
                stars = int(s)
            else:
                # map "FOUR_STAR", "THREE_STAR_SUPERIOR", etc.
                if "FIVE" in s: stars = 5
                elif "FOUR" in s: stars = 4
                elif "THREE" in s: stars = 3
                elif "TWO" in s: stars = 2
                elif "ONE" in s: stars = 1
                else:
                    stars = 0

        for offer in item.get("offers", []):
            price_total = offer.get("price", {}).get("total")

            # --- Robust board/meal plan extraction with sensible default ---
            board = (
                offer.get("boardType")
                or (offer.get("mealPlan") or {}).get("code")
                or (offer.get("mealPlan") or {}).get("type")
                or "Unknown"
            )
            # Normalise to uppercase short codes where possible
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
