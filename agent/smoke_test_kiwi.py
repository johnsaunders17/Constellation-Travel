# smoke_test_kiwi.py – Kiwi-only smoke test with IATA → City slug mapping and fallbacks

import argparse
import os
from datetime import datetime
from providers.kiwi import get_kiwi_deals

def main():
    parser = argparse.ArgumentParser(description="Kiwi smoke test")
    parser.add_argument("--origin", default="EMA", help="IATA code for origin (e.g. EMA)")
    parser.add_argument("--destination", default="ALC", help="IATA code for destination (e.g. ALC)")
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--children", type=int, default=0)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    params = {
        "origin": args.origin,
        "destination": args.destination,
        "adults": args.adults,
        "children": args.children,
        "limit": args.limit
    }

    print("=== KIWI SMOKE TEST ===")
    print("UTC:", datetime.utcnow().isoformat(), "Z")
    print(f"Origin: {params['origin']}, Destination: {params['destination']}")
    key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not key:
        print("❌ RAPIDAPI_KIWI_KEY is missing")
        return

    flights = get_kiwi_deals(params)
    print(f"Returned {len(flights)} result(s)")
    for i, f in enumerate(flights[:5], start=1):
        print(f"  {i}. £{f.get('price')} – {f.get('carrier')} – {f.get('departure')} → {f.get('arrival')}")
        if f.get("link"):
            print(f"     {f['link']}")

if __name__ == "__main__":
    main()
