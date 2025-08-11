# agent/providers/kiwi.py
import os
import requests

def get_kiwi_deals(params):
    key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not key:
        print("[Kiwi] Missing RAPIDAPI_KIWI_KEY")
        return []

    url = "https://kiwi-com-cheap-flights.p.rapidapi.com/search"  # <-- no /v2

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "kiwi-com-cheap-flights.p.rapidapi.com"
    }

    # RapidAPI version takes dd/mm/yyyy for date_from/date_to
    query = {
        "fly_from": params.get("origin", "EMA"),
        "fly_to": params.get("destination", "ALC"),
        "date_from": _to_ddmmyyyy(params["startDate"]),
        "date_to": _to_ddmmyyyy(params["startDate"]),
        "nights_in_dst_from": params.get("nights", 4),
        "nights_in_dst_to": params.get("nights", 4),
        "adults": params.get("adults", 2),
        "children": params.get("children", 0),
        "selected_cabins": "M",
        "curr": "GBP",
        "limit": 3
    }

    try:
        resp = requests.get(url, headers=headers, params=query, timeout=20)
        if resp.status_code != 200:
            print(f"[Kiwi] HTTP {resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:
        print(f"[Kiwi] API call failed: {e}")
        return []

    results = []
    for r in data:
        route = r.get("route", [])
        results.append({
            "provider": "Kiwi via RapidAPI",
            "price": r.get("price", 0),
            "carrier": (r.get("airlines") or ["?"])[0],
            "departure": route[0].get("local_departure") if route else None,
            "arrival": route[-1].get("local_arrival") if route else None,
            "link": r.get("deep_link", "")
        })

    return results

def _to_ddmmyyyy(iso_date: str) -> str:
    # "2025-08-25" -> "25/08/2025"
    y, m, d = iso_date.split("-")
    return f"{d}/{m}/{y}"
