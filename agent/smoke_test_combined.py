from datetime import datetime
from providers.amadeus_flights import search_roundtrip
from providers.amadeus_hotels import get_amadeus_hotels

params = {
    "origin": "EMA",
    "destination": "ALC",
    "destinationCityCode": "ALC",
    "startDate": "2025-08-25",
    "nights": 4,
    "adults": 2,
    "children": 0,
    "roomQuantity": 1,
    "currency": "GBP",
    "limit": 6,
    "minStars": 3,         # UI default
    "board": "HB"          # “half board”
}

print("=== COMBINED SMOKE (Flights + Hotels) ===", datetime.utcnow().isoformat(), "Z")
flights = search_roundtrip(params) or []
hotels = get_amadeus_hotels(params) or []

print(f"[Flights] {len(flights)} option(s). [Hotels] {len(hotels)} option(s).")

deals = []
for f in flights[:5]:
    for h in hotels[:10]:
        if h["price"] and f["price"]:
            if h.get("stars", 0) >= params["minStars"] and params["board"] in (h.get("board") or ""):
                per_person = (float(f["price"]) + float(h["price"])) / params["adults"]
                deals.append((per_person, f, h))

deals.sort(key=lambda x: x[0])
print(f"[Deals] {len(deals)} match(es).")
for i, (pp, f, h) in enumerate(deals[:5], start=1):
    print(f"  {i}. £{pp:.2f} pp • Flight {f['carrier']} {f['departure']} → {f['arrival']} • Hotel {h['stars']}★ {h['name']} ({h['board']})")
