import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

AMADEUS_BASE = os.getenv("AMADEUS_BASE", "https://test.api.amadeus.com")
CLIENT_ID = os.getenv("AMADEUS_API_KEY")
CLIENT_SECRET = os.getenv("AMADEUS_API_SECRET")

_TOKEN = {"value": None, "exp": 0}

# ---------- Auth ----------
def _token() -> str:
    if _TOKEN["value"] and time.time() < _TOKEN["exp"] - 60:
        return _TOKEN["value"]
    if not (CLIENT_ID and CLIENT_SECRET):
        raise RuntimeError("Missing AMADEUS_API_KEY or AMADEUS_API_SECRET")
    r = requests.post(
        f"{AMADEUS_BASE}/v1/security/oauth2/token",
        data={"grant_type": "client_credentials",
              "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    _TOKEN["value"] = data["access_token"]
    _TOKEN["exp"] = time.time() + int(data.get("expires_in", 1800))
    return _TOKEN["value"]

# ---------- Helpers ----------
def _resolve_city_code(params: dict) -> str:
    candidates = [
        params.get("destinationCityCode"),
        params.get("cityCode"),
        params.get("destinationCity"),
        params.get("destinationIata"),
        params.get("destination"),
        params.get("destinationAirport"),
    ]
    for c in candidates:
        if not c:
            continue
        s = str(c).strip().upper()
        if len(s) >= 3:
            s = s[:3]
        if s.isalpha() and len(s) == 3:
            return s
    return ""

def _parse_star_value(val) -> int:
    """Accept numeric, '3', 'THREE_STAR', etc."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        try:
            return int(val)
        except Exception:
            return 0
    s = str(val).strip().upper()
    if s.isdigit():
        return int(s)
    if "FIVE" in s: return 5
    if "FOUR" in s: return 4
    if "THREE" in s: return 3
    if "TWO" in s: return 2
    if "ONE" in s: return 1
    return 0

def _compute_checkout(check_in: str, nights: int) -> str:
    y, m, d = map(int, check_in.split("-"))
    return (datetime(y, m, d) + timedelta(days=int(nights))).date().isoformat()

# ---------- Hotel List by city (with stars capture & fallbacks) ----------
def _city_hotels_with_meta(city_code: str, radius_km: int = 30, min_stars: int = 0,
                           limit: int = 50) -> Tuple[List[str], Dict[str, int]]:
    """
    Calls /v1/reference-data/locations/hotels/by-city to get hotelIds.
    Captures any star rating present in the response and returns a map: hotelId -> stars.
    Applies resilient fallbacks (radius and param trims) for the sandbox.
    If min_stars > 0, passes ratings filter when supported by the API.
    """
    if not city_code:
        print("[Amadeus/Hotels] Missing city code; cannot query by-city.")
        return [], {}

    headers = {"Authorization": f"Bearer {_token()}"}

    def call(city: str, rad: int, use_source: bool, use_limit: bool, ratings_param: bool):
        q = {"cityCode": city, "radius": rad, "radiusUnit": "KM"}
        if use_source:
            q["hotelSource"] = "ALL"
        if use_limit:
            q["page[limit]"] = min(limit, 50)
        # If caller wants stars filtration and the endpoint supports it, send ratings list
        if ratings_param and min_stars:
            # request >=min_stars by enumerating allowed values
            stars_list = []
            for s in range(min_stars, 6):
                stars_list.append(str(s))
            q["ratings"] = ",".join(stars_list)
        return requests.get(
            f"{AMADEUS_BASE}/v1/reference-data/locations/hotels/by-city",
            headers=headers, params=q, timeout=20
        )

    # Try sequence tuned for sandbox quirks
    tries = [
        (city_code, min(max(int(radius_km), 1), 30), True, True, True),
        (city_code, 20, True, True, True),
        (city_code, 20, False, True, True),
        (city_code, 20, False, False, True),
        (city_code, 20, False, False, False),  # last: no ratings param either
    ]

    stars_map: Dict[str, int] = {}
    for city, rad, use_source, use_limit, use_ratings in tries:
        r = call(city, rad, use_source, use_limit, use_ratings)
        if r.status_code == 401:
            headers["Authorization"] = f"Bearer {_token()}"
            r = call(city, rad, use_source, use_limit, use_ratings)

        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                ids = []
                for h in data:
                    hid = h.get("hotelId")
                    if not hid:
                        continue
                    ids.append(hid)
                    # capture any rating-like field
                    # Amadeus docs: Hotel Search v3 removed rating from hotel object; Hotel List can filter by ratings.
                    # Some responses still include a 'rating' or similar numeric; capture if present.
                    star = _parse_star_value(h.get("rating") or h.get("stars") or h.get("category"))
                    if star:
                        stars_map[hid] = star
                print(f"[Amadeus/Hotels] by-city SUCCESS city={city} r={rad} source={use_source} limit={use_limit} ratings={use_ratings} -> {len(ids)} hotels")
                # If min_stars set but ratings absent, we still return ids; we will not drop them silently.
                return ids, stars_map
            # 200 but empty -> continue
        else:
            msg = r.text[:300] if hasattr(r, "text") else str(r.status_code)
            print(f"[Amadeus/Hotels] by-city {city} r={rad} (source={use_source},limit={use_limit},ratings={use_ratings}) -> {r.status_code}: {msg}")

    return [], stars_map

# ---------- Public entry point ----------
def get_amadeus_hotels(params: dict) -> list:
    """
    Flow:
      1) Hotel List by City -> hotelIds (+stars_map)
      2) Hotel Search v3 -> offers for those hotelIds
      3) Merge stars from stars_map; default board to 'UNKNOWN' when absent
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
    min_stars = int(params.get("minStars", 0))

    # Step 1: hotelIds + stars map (apply minStars at source if supported)
    hotel_ids, stars_map = _city_hotels_with_meta(city_code, radius_km=radius, min_stars=min_stars)
    if not hotel_ids:
        print(f"[Amadeus/Hotels] No hotelIds for {city_code}")
        return []

    # Step 2: one batched v3 call for offers (cap list to keep response lean)
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
        hid = hotel.get("hotelId")
        # Stars from Hotel List fallback map (v3 doesn't include hotel.rating)
        stars = int(stars_map.get(hid, 0))

        for offer in item.get("offers", []):
            price_total = offer.get("price", {}).get("total")
            board = (
                offer.get("boardType")
                or (offer.get("mealPlan") or {}).get("code")
                or (offer.get("mealPlan") or {}).get("type")
                or "UNKNOWN"
            )
            board = str(board).upper()

            # Apply minStars post-filter in case List API didn't filter
            if min_stars and stars < min_stars:
                continue

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
