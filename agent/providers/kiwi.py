import os
from datetime import datetime
import logging
import requests

logger = logging.getLogger(__name__)

def get_kiwi_deals(params):
    key = os.getenv("RAPIDAPI_KIWI_KEY")
    if not key:
        raise RuntimeError("RAPIDAPI_KIWI_KEY environment variable is not set")

    url = "https://kiwi-com-cheap-flights.p.rapidapi.com/v2/search"

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "kiwi-com-cheap-flights.p.rapidapi.com",
    }

    formatted_date = datetime.strptime(params["startDate"], "%Y-%m-%d").strftime("%d/%m/%Y")

    querystring = {
        "fly_from": params["origin"],
        "fly_to": params["destination"],
        "date_from": formatted_date,
        "date_to": formatted_date,
        "nights_in_dst_from": params["nights"],
        "nights_in_dst_to": params["nights"],
        "adults": params["adults"],
        "children": params["children"],
        "selected_cabins": "M",
        "curr": "GBP",
        "limit": 3,
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        results = response.json().get("data", [])
    except Exception:
        logger.exception("[Kiwi] API call failed")
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
