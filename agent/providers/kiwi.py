import os
import requests
from urllib.parse import quote

# Optional overrides (handy if the vendor ever changes host/path)
HOST = os.getenv("RAPIDAPI_KIWI_HOST", "kiwi-com-cheap-flights.p.rapidapi.com")
PATH = os.getenv("RAPIDAPI_KIWI_PATH", "/round-trip")
BASE_URL = f"https://{HOST}{PATH}"

# Map IATA to this vendor's City:slug format
IATA_TO_CITY = {
    "EMA": "City:nottingham_gb",
    "BHX": "City:birmingham_gb",
    "MAN": "City:manchester_gb",
    "LHR": "City:london_gb",
    "LGW": "City:london_gb",
    "STN": "City:london_gb",
    "LTN": "City:london_gb",
    "BRS": "City:bristol_gb",
    "LPL": "City:liverpool_gb",
    "ALC": "City:alicante_es",
}

# Sensible origin fallbacks to increase hit rate for GB → ES leisure routes
ORIGIN_FALLBACK_CHAIN = [
    "EMA",            # requested
    "BHX", "MAN",     # nearby major
    "LHR", "LGW",     # London catch
]

def _iata_to_city(iata: str | None) -> str | None:
    return IATA_TO_CITY.get((iata or "").upper())

def _normalise(data_item: dict) -> dict:
    price_info = data_item.get("price")
    if isinstance(price_info, dict):
        price = price_info.get("amount")
    else:
        price = price_info or data_item.get("totalPrice")

    carrier = (
        data_item.get("carrier")
        or (data_item.get("airlines")[0] if isinstance(data_item.get("airlines"), list) and data_item.get("airlines") else None)
        or data_item.get("airline")
    )

    # Try nested Tequila-style route if present
    route = data_item.get("route")
    if isinstance(route, list) and route:
        departure = route[0].get("local_departure")
        arrival = route[-1].get("local_arrival")
    else:
        departure = data_item.get("departure")
        arrival = data_item.get("arrival")

    link = data_item.get("booking_link") or data_item.get("deep_link") or ""

    return {
        "provider": "Kiwi via RapidAPI",
        "price": price,
        "carrier": carrier or "?",
        "departure": departure,
        "arrival": arrival,
        "link": link,
    }

def get_kiwi_deals(params: dict) -> list[dict]:
    """
    Calls the RapidAPI 'round-trip' endpoint with a resilient fallback chain:
    1) Try city slug that corresponds to the requested origin IATA (e.g., EMA→City:nottingham_gb)
    2) Fall back to BHX, MAN, then London catch (LHR/LGW) city slugs
    3) Finally fall back to Country:GB
    Destination tries the requested city slug (e.g., ALC→City:alicante_es) then Country:ES.

    Returns a list of normalised flight dicts or [] if nothing found.
    """
    api_key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not api_key:
        print("[Kiwi] Missing RAPIDAPI_KIWI_KEY")
        return []

    # Headers
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": HOST,
    }

    # Build candidate origins
    requested_origin_iata = (params.get("origin") or "EMA").upper()
    origin_candidates_iata = [requested_origin_iata] + [c for c in ORIGIN_FALLBACK_CHAIN if c != requested_origin_iata]

    origin_candidates = []
    for iata in origin_candidates_iata:
        city = _iata_to_city(iata)
        if city:
            origin_candidates.append(city)
    # Ensure country-level last
    origin_candidates.append("Country:GB")

    # Build candidate destinations
    requested_dest_iata = (params.get("destination") or "ALC").upper()
    dest_candidates = []
    dest_city = _iata_to_city(requested_dest_iata)
    if dest_city:
        dest_candidates.append(dest_city)
    # Ensure country-level last
    dest_candidates.append("Country:ES")

    # Base query (mirrors vendor playground flags; avoid over-filtering)
    base_query = {
        "currency": "gbp",
        "locale": "en",
        "adults": params.get("adults", 2),
        "children": params.get("children", 0),
        "infants": 0,
        "handbags": 1,
        "holdbags": 0,
        "cabinClass": "ECONOMY",
        "sortBy": "QUALITY",
        "sortOrder": "ASCENDING",
        "applyMixedClasses": "true",
        "allowReturnFromDifferentCity": "true",
        "allowChangeInboundDestination": "true",
        "allowChangeInboundSource": "true",
        "allowDifferentStationConnection": "true",
        "enableSelfTransfer": "true",
        "allowOvernightStopover": "true",
        "enableTrueHiddenCity": "true",
        "enableThrowAwayTicketing": "true",
        "outbound": "SUNDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY,MONDAY,TUESDAY",
        "transportTypes": "FLIGHT",
        "contentProviders": "KIWI",
        "limit": params.get("limit", 5),
    }

    # Try combinations until we get non-empty data
    for src in origin_candidates:
        for dst in dest_candidates:
            q = base_query.copy()
            # Some vendors require these to be URL-encoded; quote() avoids issues with ":" and "_"
            q["source"] = quote(src, safe="")
            q["destination"] = quote(dst, safe="")

            try:
                resp = requests.get(BASE_URL, headers=headers, params=q, timeout=25)
                if resp.status_code != 200:
                    # Soft-fail and try the next combo
                    print(f"[Kiwi] HTTP {resp.status_code} for {src} -> {dst}")
                    continue

                payload = resp.json()
                data = payload.get("data", payload if isinstance(payload, list) else [])
                if not data:
                    print(f"[Kiwi] 200 OK but empty for {src} -> {dst}")
                    continue

                # Return first non-empty result set
                results = [_normalise(item) for item in data]
                print(f"[Kiwi] Found {len(results)} result(s) for {src} -> {dst}")
                return results

            except Exception as e:
                print(f"[Kiwi] Error for {src} -> {dst}: {e}")
                continue

    # If we reach here, nothing matched across all fallbacks
    print("[Kiwi] No results across all fallbacks.")
    return []
