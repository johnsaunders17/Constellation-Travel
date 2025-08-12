import os
import requests
from urllib.parse import quote

# Map IATA codes to this RapidAPI product's City:slug format
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
    "ALC": "City:alicante_es"
}

def get_kiwi_deals(params):
    """Fetch flight deals via RapidAPI with fallback logic.

    We attempt city-level queries first and fall back to country-level.
    """
    api_key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not api_key:
        print("[Kiwi] Missing RAPIDAPI_KIWI_KEY")
        return []

    host = "kiwi-com-cheap-flights.p.rapidapi.com"
    path = "/round-trip"
    url = f"https://{host}{path}"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }

    # Build candidate origin/destination selectors
    origin_iata = params.get("origin", "EMA").upper()
    dest_iata = params.get("destination", "ALC").upper()
    city_origin = IATA_TO_CITY.get(origin_iata)
    city_dest = IATA_TO_CITY.get(dest_iata)

    # Try city slug if available, then fallback to country
    sources = [s for s in (city_origin, f"Country:GB") if s]
    destinations = [d for d in (city_dest, f"Country:ES") if d]

    # Core RapidAPI flags (mirrors the playground example)
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
        "limit": params.get("limit", 5)
    }

    # Try each source/destination combination until we get data
    for src in sources:
        for dst in destinations:
            query = base_query.copy()
            query["source"] = quote(src, safe="")
            query["destination"] = quote(dst, safe="")
            try:
                response = requests.get(url, headers=headers, params=query, timeout=20)
                if response.status_code != 200:
                    # If 404 or other errors, continue to next combination
                    print(f"[Kiwi] HTTP {response.status_code} on {src}->{dst}")
                    continue
                data = response.json().get("data", [])
                if not data:
                    continue
                # Normalise result fields
                results = []
                for item in data:
                    price_info = item.get("price")
                    if isinstance(price_info, dict):
                        price = price_info.get("amount")
                    else:
                        price = price_info or item.get("totalPrice")
                    carrier = (
                        item.get("carrier") or
                        (item.get("airlines")[0] if item.get("airlines") else None) or
                        item.get("airline")
                    )
                    dep = item.get("departure") or _nested(item, first=True)
                    arr = item.get("arrival") or _nested(item, first=False)
                    results.append({
                        "provider": "Kiwi via RapidAPI",
                        "price": price,
                        "carrier": carrier,
                        "departure": dep,
                        "arrival": arr,
                        "link": item.get("booking_link") or item.get("deep_link") or ""
                    })
                return results
            except Exception as e:
                print(f"[Kiwi] Error on {src}->{dst}: {e}")
                continue

    # No results for any combination
    return []

def _nested(item, first=True):
    route = item.get("route")
    if isinstance(route, list) and route:
        leg = route[0] if first else route[-1]
        return leg.get("local_departure") if first else leg.get("local_arrival")
    return None
