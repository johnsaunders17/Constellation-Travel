from datetime import datetime
from providers.amadeus_hotels import get_amadeus_hotels

params = {
    "destinationCityCode": "ALC",
    "startDate": "2025-08-25",
    "nights": 4,
    "adults": 2,
    "roomQuantity": 1,
    "currency": "GBP",
    "radius": 30
}

print("=== AMADEUS HOTELS SMOKE ===", datetime.utcnow().isoformat(), "Z")
hotels = get_amadeus_hotels(params)
print(f"Returned {len(hotels)} option(s).")
for i, h in enumerate(hotels[:5], start=1):
    print(f"  {i}. £{h.get('price')} • {h.get('stars')}★ • {h.get('board')} • {h.get('name')}")
