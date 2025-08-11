# agent/smoke_test_kiwi.py
# Purpose: Minimal Kiwi-only smoke test for the RapidAPI product that exposes /round-trip
# It proves your RAPIDAPI_KIWI_KEY works and that the endpoint/params are correct.

import os
import sys
import argparse
import json
from datetime import datetime
import requests


HOST = "kiwi-com-cheap-flights.p.rapidapi.com"
PATH = "/round-trip"
BASE_URL = f"https://{HOST}{PATH}"


def main():
    parser = argparse.ArgumentParser(description="Kiwi-only smoke test via RapidAPI /round-trip")
    parser.add_argument("--source", default="City:nottingham_gb",
                        help="Origin selector, e.g. 'City:nottingham_gb' or 'Country:GB'")
    parser.add_argument("--destination", default="City:alicante_es",
                        help="Destination selector, e.g. 'City:alicante_es'")
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--children", type=int, default=0)
    parser.add_argument("--currency", default="gbp")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    api_key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not api_key:
        print("❌ Missing environment variable: RAPIDAPI_KIWI_KEY")
        sys.exit(1)

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": HOST
    }

    # Parameters aligned to the vendor’s Playground snippet
    params = {
        "source": args.source,                 # e.g. City:nottingham_gb  or Country:GB
        "destination": args.destination,       # e.g. City:alicante_es
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
        # Outbound days of week as per the Playground example
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

    try:
        resp = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code}")
            txt = resp.text
            print(txt[:1000] if txt else "<no body>")
            sys.exit(2)
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        sys.exit(2)

    # The response shape can vary by vendor; handle a few common patterns.
    try:
        payload = resp.json()
    except json.JSONDecodeError:
        print("❌ Response was not JSON:")
        print(resp.text[:1000])
        sys.exit(2)

    data = []
    if isinstance(payload, dict) and "data" in payload:
        data = payload["data"]
    elif isinstance(payload, list):
        data = payload
    else:
        print("⚠️ Unexpected response shape. Top-level keys:", list(payload)[:10])

    print(f"Returned {len(data)} item(s).")
    for i, item in enumerate(data[:5], start=1):
        price = (
            (item.get("price", {}) or {}).get("amount")
            if isinstance(item.get("price"), dict)
            else item.get("price") or item.get("totalPrice")
        )
        carrier = item.get("carrier") or _first(item.get("airlines")) or item.get("airline") or "?"
        dep = item.get("departure") or _nested_route(item, first=True)
        arr = item.get("arrival") or _nested_route(item, first=False)
        link = item.get("booking_link") or item.get("deep_link") or ""
        print(f"  {i}. £{price} • {carrier} • {dep} → {arr}")
        if link:
            print(f"     link: {link}")

    if not data:
        print("\nNo results. Typical causes:")
        print("- Endpoint parameters don’t match the vendor’s expectations.")
        print("- Try broader selectors: --source 'Country:GB'  --destination 'Country:ES'")
        print("- Reduce limit: --limit 1")
        print("- Rate limits on RapidAPI; wait a few minutes and retry.")

def _first(x):
    if isinstance(x, list) and x:
        return x[0]
    return None

def _nested_route(item, first=True):
    """
    Some vendors return nested segments like Tequila.
    We try to pull a 'local_departure' or 'local_arrival' if they exist.
    """
    route = item.get("route")
    if isinstance(route, list) and route:
        leg = route[0] if first else route[-1]
        return leg.get("local_departure") if first else leg.get("local_arrival")
    return None


if __name__ == "__main__":
    main()
