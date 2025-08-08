import os
import requests
from datetime import datetime, timedelta

print("🔐 Testing Amadeus authentication...")

token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
client_id = os.getenv("AMADEUS_API_KEY")
client_secret = os.getenv("AMADEUS_API_SECRET")

auth_res = requests.post(
    token_url,
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    },
    headers={ "Content-Type": "application/x-www-form-urlencoded" }
)

if auth_res.status_code != 200:
    print("❌ Auth failed:", auth_res.status_code, auth_res.text)
    exit(1)

token = auth_res.json()["access_token"]
print("✅ Amadeus token acquired")

# Minimal test: fetch hotel offers
check_in = datetime.today().strftime("%Y-%m-%d")
check_out = (datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")

print("🏨 Testing hotel lookup (Alicante)...")
offers_url = "https://test.api.amadeus.com/v2/shopping/hotel-offers"
offers_res = requests.get(
    offers_url,
    headers={ "Authorization": f"Bearer {token}" },
    params={
        "cityCode": "ALC",
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "adults": 2,
        "roomQuantity": 1,
        "radius": 30,
        "radiusUnit": "KM",
        "currency": "GBP"
    }
)

if offers_res.status_code != 200:
    print("❌ Hotel lookup failed:", offers_res.status_code, offers_res.text)
else:
    hotels = offers_res.json().get("data", [])
    print(f"✅ Found {len(hotels)} hotel result(s)")
    if hotels:
        first = hotels[0]
        print("🏨 Sample:", first["hotel"]["name"], "-", first["offers"][0]["price"])
