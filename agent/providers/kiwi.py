import os
import requests

def get_kiwi_deals(params):
    key = os.getenv("RAPIDAPI_KIWI_KEY")
    url = "https://kiwi-com-cheap-flights.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "kiwi-com-cheap-flights.p.rapidapi.com"
    }

    querystring = {
        "fly_from": params["origin"],
        "fly_to": params["destination"],
        "date_from": params["startDate"],
        "date_to": params["startDate"],
        "nights_in_dst_from": params["nights"],
        "nights_in_dst_to": params["nights"],
        "adults": params["adults"],
        "children": params["children"],
        "selected_cabins": "M",
        "curr": "GBP",
        "limit": 3
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        results = response.json().get("data", [])
    except Exception as e:
        print(f"[Kiwi] API call failed: {e}")
        return []

    output = []
    for r in results:
        output.append({
            "provider": "Kiwi via RapidAPI",
            "price": r.get("price", 0),
            "carrier": r.get("airlines", ["N/A"])[0],
            "departure": r.get("route", [{}])[0].get("local_departure"),
            "arrival": r.get("route", [{}])[-1].get("local_arrival"),
            "link": r.get("deep_link", "")
        })

    return output
