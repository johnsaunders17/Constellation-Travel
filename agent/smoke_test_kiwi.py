# agent/smoke_test_kiwi.py
import os, sys, argparse, json, time
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HOST = "kiwi-com-cheap-flights.p.rapidapi.com"
PATH = "/round-trip"
BASE_URL = f"https://{HOST}{PATH}"

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

def map_origin_dest(origin: str|None, dest: str|None, fallback_source: str, fallback_dest: str):
    s = IATA_TO_CITY.get((origin or "").upper(), fallback_source)
    d = IATA_TO_CITY.get((dest or "").upper(), fallback_dest)
    return s, d

def parse_args():
    p = argparse.ArgumentParser(description="Kiwi-only smoke test via RapidAPI /round-trip")
    # RapidAPI-native
    p.add_argument("--source", help="e.g. 'City:nottingham_gb' or 'Country:GB'")
    p.add_argument("--destination", help="e.g. 'City:alicante_es' or 'Country:ES'")
    p.add_argument("--adults", type=int, default=2)
    p.add_argument("--children", type=int, default=0)
    p.add_argument("--currency", default="gbp")
    p.add_argument("--limit", type=int, default=3)  # lower default to reduce payload
    p.add_argument("--raw", action="store_true", help="dump first 800 chars of body for debugging")
    # Back-compat flags (ignored by this endpoint except for mapping)
    p.add_argument("--origin")
    p.add_argument("--startDate")
    p.add_argument("--nights")
    return p.parse_args()

def session_with_retries(total=3, backoff=0.8):
    retry = Retry(
        total=total,
        connect=total,
        read=total,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"])
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s

def main():
    args = parse_args()

    api_key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not api_key:
        print("❌ Missing environment variable: RAPIDAPI_KIWI_KEY")
        sys.exit(1)

    src = args.source
    dst = args.destination
    if not (src and dst):
        # If native not provided, map IATA→vendor slugs, else fall back to Country
        src, dst = map_origin_dest(args.origin, args.destination, "Country:GB", "Country:ES")

    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": HOST}
    params = {
        "source": src,
        "destination": dst,
        "currency": args.currency,
        "locale": "en",
        "adults": args.adults,
        "children": args.children,
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
        "limit": args.limit
    }

    print("=== KIWI SMOKE TEST (RapidAPI /round-trip) ===")
    print("UTC:", datetime.utcnow().isoformat(), "Z")
    print(f"Endpoint: {BASE_URL}")
    print(f"Params: source='{params['source']}', destination='{params['destination']}', "
          f"adults={params['adults']}, children={params['children']}, currency={params['currency']}, limit={params['limit']}")
    print()

    s = session_with_retries(total=3, backoff=0.9)
    try:
        resp = s.get(BASE_URL, headers=headers, params=params, timeout=12)  # faster fail, retries handle bursts
        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code}")
            if args.raw:
                print(resp.text[:800])
            sys.exit(2)
    except requests.RequestException as e:
        print(f"❌ Request failed after retries: {e}")
        sys.exit(2)

    if args.raw:
        print("[RAW]", resp.text[:800])

    try:
        payload = resp.json()
    except json.JSONDecodeError:
        print("❌ Response was not JSON:")
        print(resp.text[:800])
        sys.exit(2)

    data = payload.get("data", payload if isinstance(payload, list) else [])
    print(f"Returned {len(data)} item(s).")
    for i, item in enumerate(data[:5], start=1):
        price = ((item.get("price") or {}).get("amount")
                 if isinstance(item.get("price"), dict)
                 else item.get("price") or item.get("totalPrice"))
        carrier = (item.get("carrier")
                   or (item.get("airlines")[0] if isinstance(item.get("airlines"), list) and item.get("airlines") else "?")
                   or item.get("airline") or "?")
        dep = item.get("departure") or _nested_route(item, first=True)
        arr = item.get("arrival") or _nested_route(item, first=False)
        link = item.get("booking_link") or item.get("deep_link") or ""
        print(f"  {i}. £{price} • {carrier} • {dep} → {arr}")
        if link:
            print(f"     link: {link}")

    if not data:
        print("\nNo results. Try:")
        print("- Broader selectors: --source 'Country:GB' --destination 'Country:ES'")
        print("- Different city mapping: --origin BHX or --source 'City:birmingham_gb'")
        print("- Lower limit: --limit 1 (mitigate payload and rate limits)")
        print("- Add --raw to inspect the first 800 chars of the response body")

def _nested_route(item, first=True):
    route = item.get("route")
    if isinstance(route, list) and route:
        leg = route[0] if first else route[-1]
        return leg.get("local_departure") if first else leg.get("local_arrival")
    return None

if __name__ == "__main__":
    main()
