import os
import requests
from urllib.parse import quote

def get_kiwi_deals(params):
    key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not key:
        print("[Kiwi] Missing RAPIDAPI_KIWI_KEY")
        return []

    host = "kiwi-com-cheap-flights.p.rapidapi.com"
    path = "/round-trip"
    url = f"https://{host}{path}"

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": host
    }

    # Map our params to this API's expected querystring
    # Your snippet uses e.g., Country:GB or City:alicante_es
    # We’ll assume direct city search for flights to Alicante (ALC)
    source = f"City:{params.get('originCityCode', 'nottingham_gb')}"  # Example; you might use Country:GB
    destination = f"City:{params.get('destinationCityCode', 'alicante_es')}"

    query = {
        "source": quote(source, safe=""),
        "destination": quote(destination, safe=""),
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
        "limit": 5
    }

    try:
        resp = requests.get(url, headers=headers, params=query, timeout=20)
        if resp.status_code != 200:
            print(f"[Kiwi] HTTP {resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:
        print(f"[Kiwi] API call failed: {e}")
        return []

    results = []
    for r in data:
        # This API's schema may differ — adjust as needed
        results.append({
            "provider": "Kiwi via RapidAPI",
            "price": r.get("price", {}).get("amount") if isinstance(r.get("price"), dict) else r.get("price"),
            "carrier": r.get("carrier", "Unknown"),
            "departure": r.get("departure"),
            "arrival": r.get("arrival"),
            "link": r.get("booking_link", "")
        })

    return results
