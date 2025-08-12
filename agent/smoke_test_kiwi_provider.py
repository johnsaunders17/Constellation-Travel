from datetime import datetime
from providers.kiwi import get_kiwi_deals

params = {
    "origin": "EMA",
    "destination": "ALC",
    "adults": 2,
    "children": 0,
    "limit": 3
}

print("=== KIWI PROVIDER SMOKE ===", datetime.utcnow().isoformat(), "Z")
flights = get_kiwi_deals(params)
print(f"Returned {len(flights)} result(s)")
for i, f in enumerate(flights[:5], start=1):
    print(f"  {i}. £{f.get('price')} – {f.get('carrier')} – {f.get('departure')} → {f.get('arrival')}")
