# agent/smoke_test_kiwi.py
# Purpose: mirror the RapidAPI sandbox "round-trip" request that returned results.

import os
import sys
import argparse
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HOST = "kiwi-com-cheap-flights.p.rapidapi.com"
PATH = "/round-trip"
BASE_URL = f"https://{HOST}{PATH}"

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

def parse_args():
    p = argparse.ArgumentParser(description="Kiwi RapidAPI /round-trip smoke test (mirrors sandbox call)")
    p.add_argument("--source", default="Country:GB")
    p.add_argument("--destination", default="Country:ES")
    p.add_argument("--currency", default="gbp")
    p.add_argument("--adults", type=int, default=1)
    p.add_argument("--children", type=int, default=0)
    p.add_argument("--infants", type=int, default=0)
    p.add_argument("--limit", type=int, default=20)

    # Dates as per sandbox. Note: sandbox uses a *typo* key: outboundDepartmentDateStart.
    # We’ll send BOTH keys to be safe.
    p.add_argument("--inboundDepartureDateStart", default="2025-08-26")
    p.add_argument("--outboundDepartureDateStart", default="2025-09-02")  # the correct-looking key
    p.add_argument("--outboundDepartmentDateStart", default=None)         # the sandbox-typo key

    p.add_argument("--raw", action="store_true", help="Print first 800 chars of response")
    return p.parse_args()

def main():
    args = parse_args()

    api_key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not api_key:
        print("❌ Missing RAPIDAPI_KIWI_KEY")
        sys.exit(1)

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": HOST
    }

    params = {
        # Route & currency (broad like the sandbox)
        "source": args.source,
        "destination": args.destination,
        "currency": args.currency,
        "locale": "en",

        # Pax & baggage
        "adults": args.adults,
        "children": args.children,
        "infants": args.infants,
        "handbags": 1,
        "holdbags": 0,
        "cabinClass": "ECONOMY",

        # Sorting & behaviour flags (copied from your sandbox)
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

        # Days of week & transport/providers (broaden coverage)
        "outbound": "SUNDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY,MONDAY,TUESDAY",
        "transportTypes": "FLIGHT",
        "contentProviders": "FLIXBUS_DIRECTS,FRESH,KAYAK,KIWI",

        "limit": args.limit,

        # Date controls (send both keys for outbound to mirror sandbox exactly)
        "inboundDepartureDateStart": args.inboundDepartureDateStart,
        "outboundDepartureDateStart": args.outboundDepartureDateStart
    }

    if args.outboundDepartmentDateStart:  # typo key used by sandbox; include if provided
        params["outboundDepartmentDateStart"] = args.outboundDepartmentDateStart

    print("=== KIWI SMOKE TEST (RapidAPI /round-trip; sandbox parity) ===")
    print("UTC:", datetime.utcnow().isoformat(), "Z")
    print(f"Endpoint: {BASE_URL}")
    print(f"Params: source='{params['source']}', destination='{params['destination']}', "
          f"currency={params['currency']}, adults={params['adults']}, children={params['children']}, limit={params['limit']}")
    print(f"Dates: inboundDepartureDateStart={params['inboundDepartureDateStart']}, "
          f"outboundDepartureDateStart={params.get('outboundDepartureDateStart')}, "
          f"outboundDepartmentDateStart={params.get('outboundDepartmentDateStart')}")
    print()

    s = session_with_retries(total=3, backoff=0.9)
    try:
        resp = s.get(BASE_URL, headers=headers, params=params, timeout=12)
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

    # Parse & print a quick summary
    try:
        payload = resp.json()
    except Exception:
        print("❌ Response not JSON:")
        print(resp.text[:800])
        sys.exit(2)

    data = payload.get("data", payload if isinstance(payload, list) else [])
    print(f"Returned {len(data)} item(s).")
    for i, item in enumerate(data[:5], start=1):
        # Try to normalise common fields defensively
        price = (
            (item.get("price") or {}).get("amount")
            if isinstance(item.get("price"), dict)
            else item.get("price") or item.get("totalPrice")
        )
        carrier = (item.get("carrier")
                   or (item.get("airlines")[0] if isinstance(item.get("airlines"), list) and item.get("airlines") else "?")
                   or item.get("airline") or "?")
        dep = item.get("departure")
        arr = item.get("arrival")
        link = item.get("booking_link") or item.get("deep_link") or ""
        print(f"  {i}. £{price} • {carrier} • {dep} → {arr}")
        if link:
            print(f"     {link}")

if __name__ == "__main__":
    main()
