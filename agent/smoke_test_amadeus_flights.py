from datetime import datetime
from providers.amadeus_flights import search_roundtrip

params = {
    "origin": "EMA",
    "destination": "ALC",
    "startDate": "2025-08-25",
    "nights": 4,
    "adults": 2,
    "children": 0,
    "currency": "GBP",
    "limit": 6
}

print("=== AMADEUS FLIGHTS SMOKE ===", datetime.utcnow().isoformat(), "Z")
flights = search_roundtrip(params)
print(f"Returned {len(flights)} option(s).")
for i, f in enumerate(flights[:5], start=1):
    print(f"  {i}. £{f.get('price')} • {f.get('carrier')} • {f.get('departure')} → {f.get('arrival')}")
