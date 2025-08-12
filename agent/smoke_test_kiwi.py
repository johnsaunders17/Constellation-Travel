# agent/smoke_test_kiwi.py
# Mirrors RapidAPI sandbox for /round-trip and stays backwards-compatible with legacy flags.

import os, sys, argparse, json
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HOST = "kiwi-com-cheap-flights.p.rapidapi.com"
PATH = "/round-trip"
BASE_URL = f"https://{HOST}{PATH}"

# Minimal IATA→City mapping (used only if --source/--destination not provided)
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

def map_iata_to_vendor(origin_iata, dest_iata):
    src = IATA_TO_CITY.get((origin_iata or "").upper(), "Country:GB")
    dst = IATA_TO_CITY.get((dest_iata or "").upper(), "Country:ES")
    return src, dst

def session_with_retries(total=3, backoff=0.8):
    retry = Retry(
        total=total,
        connect=total,
        read=total,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s

def parse_args():
    p = argparse.ArgumentParser(description="Kiwi RapidAPI /round-trip smoke test (sandbox parity + legacy flags)")
    # Native sandbox-style params
    p.add_argument("--source", default=None, help="e.g. 'Country:GB' or 'City:birmingham_gb'")
    p.add_argument("--destination", default=None, help="e.g. 'Country:ES' or 'City:alicante_es'")
    p.add_argument("--currency", default="gbp")
    p.add_argument("--adults", type=int, default=1)
    p.add_argument("--children", type=int, default=0)
    p.add_argument("--infants", type=int, default=0)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--inboundDepartureDateStart", default=None)
    p.add_argument("--outboundDepartureDateStart", default=None)
    # The sandbox typo; we’ll send it if provided or if we compute dates
    p.add_argument("--outboundDepartmentDateStart", default=None)
    p.add_argument("--raw", action="store_true")

    # Legacy flags (back-compat). If used, we compute the date params.
    p.add_argument("--origin", default=None, help="IATA (e.g. EMA)")
    p.add_argument("--destinationIata", dest="destination_iata", default=None, help="IATA (e.g. ALC)")
    p.add_argument("--destinationLegacy", dest="destination_legacy", default=None, help="Alias of --destinationIata")
    p.add_argument("--destination", default=None, help="Used as either IATA (legacy) or vendor slug (native)")
    p.add_argument("--startDate", default=None, help="YYYY-MM-DD")
    p.add_argument("--nights", default=None, help="Integer nights")
    return p.parse_args()

def compute_dates_if_needed(args):
    """
    If legacy startDate/nights are given and sandbox-style params are missing,
    compute and set:
      inboundDepartureDateStart = startDate
      outboundDepartureDateStart = startDate + nights
      outboundDepartmentDateStart = same as outboundDepartureDateStart (typo key)
    """
    if not args.startDate or not args.nights:
        return None, None, None
    try:
        nights_int = int(args.nights)
        y, m, d = args.startDate.split("-")
        out_date = (datetime(int(y), int(m), int(d)) + timedelta(days=nights_int)).date().isoformat()
        return args.startDate, out_date, out_date
    except Exception:
        return None, None, None

def main():
    args = parse_args()

    api_key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not api_key:
        print("❌ Missing RAPIDAPI_KIWI_KEY")
        sys.exit(1)

    # Resolve route parameters:
    # Priority 1: native --source/--destination
    src = args.source
    dst = args.destination

    # If not provided, try legacy IATA mapping
    if not (src and dst):
        # destination might be provided under different names; prefer explicit native if looks like City:/Country:
        if args.origin or args.destination_iata or (args.destination and ":" not in args.destination):
            iata_dest = args.destination_iata or args.destination_legacy or args.destination
            src, dst = map_iata_to_vendor(args.origin, iata_dest)

    # Final hard defaults if still missing
    src = src or "Country:GB"
    dst = dst or "Country:ES"

    # Dates: honour explicit sandbox params; if missing and we have legacy startDate/nights, compute them.
    in_start = args.inboundDepartureDateStart
    out_start = args.outboundDepartureDateStart
    out_typo = args.outboundDepartmentDateStart

    if not (in_start and (out_start or out_typo)) and args.startDate and args.nights:
        calc_in, calc_out, calc_typo = compute_dates_if_needed(args)
        in_start = in_start or calc_in
        out_start = out_start or calc_out
        out_typo = out_typo or calc_typo

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": HOST,
    }

    params = {
        "source": src,
        "destination": dst,
        "currency": args.currency,
        "locale": "en",
        "adults": args.adults,
        "children": args.children,
        "infants": args.infants,
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
        "contentProviders": "FLIXBUS_DIRECTS,FRESH,KAYAK,KIWI",
        "limit": args.limit,
    }

    # Add date filters if available (send BOTH outbound keys if we have them)
    if in_start:
        params["inboundDepartureDateStart"] = in_start
    if out_start:
        params["outboundDepartureDateStart"] = out_start
    if out_typo:
        params["outboundDepartmentDateStart"] = out_typo

    print("=== KIWI SMOKE TEST (RapidAPI /round-trip; sandbox parity) ===")
    print("UTC:", datetime.utcnow().isoformat(), "Z")
    print(f"Endpoint: {BASE_URL}")
    print(f"Params: source='{params['source']}', destination='{params['destination']}', "
          f"currency={params['currency']}, adults={params['adults']}, children={params['children']}, limit={params['limit']}")
    print(f"Dates: inboundDepartureDateStart={params.get('inboundDepartureDateStart')}, "
          f"outboundDepartureDateStart={params.get('outboundDepartureDateStart')}, "
          f"outboundDepartmentDateStart={params.get('outboundDepartmentDateStart')}")
    print()

    s = session_with_retries(total=3, backoff=0.9)
    try:
        resp = s.get(BASE_URL, headers=headers, params=params, timeout=12)
        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code}")
            print(resp.text[:800])
            sys.exit(2)
    except requests.RequestException as e:
        print(f"❌ Request failed after retries: {e}")
        sys.exit(2)

    if args.raw:
        print("[RAW]", resp.text[:800])

    # Parse results
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
        dep = item.get("departure")
        arr = item.get("arrival")
        link = item.get("booking_link") or item.get("deep_link") or ""
        print(f"  {i}. £{price} • {carrier} • {dep} → {arr}")
        if link:
            print(f"     {link}")

if __name__ == "__main__":
    main()
