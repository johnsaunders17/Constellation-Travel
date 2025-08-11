# agent/smoke_test.py
import os
from datetime import datetime, timedelta

from providers.kiwi import get_kiwi_deals
from providers.amadeus import get_amadeus_hotels

PARAMS = {
    "origin": "EMA",
    "destination": "ALC",
    "startDate": "2025-08-25",
    "nights": 4,
    "adults": 2,
    "children": 0,
    "board": "HB",
    "minStars": 3,          # keep loose for smoke test
    "budgetPerPerson": 9999 # disable budget gating for now
}

def main():
    print("=== SMOKE TEST START ===")
    print("Date:", datetime.utcnow().isoformat(), "Z")
    print("Origin:", PARAMS["origin"], "Destination:", PARAMS["destination"])
    print()

    # --- Kiwi (RapidAPI) ---
    print("[KIWI] Testing flight search…")
    flights = get_kiwi_deals(PARAMS)
    print(f"[KIWI] Returned {len(flights)} option(s)")
    if flights[:3]:
        for i, f in enumerate(flights[:3], start=1):
            print(f"  {i}. £{f.get('price')} • {f.get('carrier')} • {f.get('departure')} → {f.get('arrival')}")
    else:
        print("  No flights found (check dates, API key, or rate limits).")
    print()

    # --- Amadeus ---
    print("[AMADEUS] Testing hotel search…")
    hotels = get_amadeus_hotels(PARAMS)
    print(f"[AMADEUS] Returned {len(hotels)} option(s)")
    if hotels[:5]:
        for i, h in enumerate(hotels[:5], start=1):
            print(f"  {i}. £{h.get('price')} • {h.get('stars')}★ • {h.get('board')} • {h.get('name')}")
    else:
        print("  No hotels found (can be normal with test data—check logs for 200s and JSON).")

    print("\n=== SMOKE TEST END ===")

if __name__ == "__main__":
    main()
