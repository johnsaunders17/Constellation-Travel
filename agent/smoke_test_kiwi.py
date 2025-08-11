# Kiwi-only smoke test
# Runs a single search via your RapidAPI Kiwi provider and prints the top few results.

import os
import argparse
from datetime import datetime
from providers.kiwi import get_kiwi_deals

DEFAULTS = {
    "origin": "EMA",        # East Midlands
    "destination": "ALC",   # Alicante
    "startDate": "2025-08-25",
    "nights": 4,
    "adults": 2,
    "children": 0,
    "board": "HB",          # ignored by Kiwi; kept for shape consistency
    "minStars": 3,          # ignored here
    "budgetPerPerson": 9999 # ignored here
}

def main():
    parser = argparse.ArgumentParser(description="Kiwi-only smoke test")
    parser.add_argument("--origin", default=DEFAULTS["origin"])
    parser.add_argument("--destination", default=DEFAULTS["destination"])
    parser.add_argument("--startDate", default=DEFAULTS["startDate"])  # YYYY-MM-DD
    parser.add_argument("--nights", type=int, default=DEFAULTS["nights"])
    parser.add_argument("--adults", type=int, default=DEFAULTS["adults"])
    parser.add_argument("--children", type=int, default=DEFAULTS["children"])
    args = parser.parse_args()

    params = {
        "origin": args.origin,
        "destination": args.destination,
        "startDate": args.startDate,
        "nights": args.nights,
        "adults": args.adults,
        "children": args.children,
        "board": "HB",
        "minStars": 3,
        "budgetPerPerson": 9999
    }

    print("=== KIWI SMOKE TEST ===")
    print("UTC time:", datetime.utcnow().isoformat(), "Z")
    print(f"Route: {params['origin']} → {params['destination']}")
    print(f"Date:  {params['startDate']}  Nights: {params['nights']}  Pax: A{params['adults']}/C{params['children']}")
    print()

    key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not key:
        print("❌ Missing RAPIDAPI_KIWI_KEY environment variable.")
        return

    flights = get_kiwi_deals(params)
    print(f"Returned {len(flights)} option(s).")

    for i, f in enumerate(flights[:5], start=1):
        price = f.get("price")
        carrier = f.get("carrier")
        dep = f.get("departure")
        arr = f.get("arrival")
        print(f"  {i}. £{price} • {carrier} • {dep} → {arr}")

    if not flights:
        print("\nNo results. Typical causes:")
        print("- RapidAPI rate limit (HTTP 429) – wait a few minutes and retry.")
        print("- Endpoint path wrong – ensure kiwi.py uses '/search' (no '/v2').")
        print("- Date availability – try a nearby date or origin (e.g., BHX/MAN).")

if __name__ == "__main__":
    main()
