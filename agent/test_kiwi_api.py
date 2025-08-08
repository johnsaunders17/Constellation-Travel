import os
import requests
from datetime import datetime

print("🔐 Testing Kiwi via RapidAPI...")

url = "https://kiwi-com-cheap-flights.p.rapidapi.com/search"

headers = {
    "X-RapidAPI-Key": os.getenv("RAPIDAPI_KIWI_KEY"),
    "X-RapidAPI-Host": "kiwi-com-cheap-flights.p.rapidapi.com"
}

today = datetime.today().strftime("%d/%m/%Y")

params = {
    "fly_from": "EMA",
    "fly_to": "ALC",
    "date_from": today,
    "date_to": today,
    "adults": 2,
    "curr": "GBP",
    "limit": 3
}

res = requests.get(url, headers=headers, params=params)

if res.status_code != 200:
    print("❌ Kiwi API failed:", res.status_code, res.text)
else:
    flights = res.json().get("data", [])
    print(f"✅ Found {len(flights)} flight(s)")
    if flights:
        f = flights[0]
        print("✈️  Sample:", f.get("airlines", ["?"])[0], f.get("price"), "GBP")
