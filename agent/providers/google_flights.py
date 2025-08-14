import os
import requests
from datetime import datetime, timedelta

# RapidAPI Google Flights configuration
HOST = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_HOST", "google-flights-search.p.rapidapi.com")
BASE_URL = f"https://{HOST}"

def _normalize_flight_data(flight_data: dict) -> dict:
    """Normalize Google Flights data to match our standard format"""
    try:
        # Extract price information
        price_info = flight_data.get("price", {})
        if isinstance(price_info, dict):
            price = price_info.get("amount") or price_info.get("total")
        else:
            price = price_info
        
        # Extract airline information
        airline = flight_data.get("airline") or flight_data.get("carrier")
        if isinstance(airline, list):
            airline = airline[0] if airline else "Unknown"
        
        # Extract route information
        route = flight_data.get("route", {})
        departure = route.get("departure") or route.get("departureTime")
        arrival = route.get("arrival") or route.get("arrivalTime")
        
        # Extract booking link
        link = flight_data.get("bookingLink") or flight_data.get("deepLink") or ""
        
        return {
            "provider": "Google Flights via RapidAPI",
            "price": float(price) if price else 0.0,
            "carrier": airline or "Unknown",
            "departure": departure,
            "arrival": arrival,
            "link": link,
            "duration": flight_data.get("duration"),
            "stops": flight_data.get("stops", 0)
        }
    except Exception as e:
        print(f"[ERROR] Failed to normalize Google Flights data: {e}")
        return {}

def search_google_flights(params: dict) -> list[dict]:
    """
    Search for flights using Google Flights via RapidAPI
    
    Args:
        params: Dictionary containing search parameters
            - origin: Origin airport code (e.g., "EMA")
            - destination: Destination airport code (e.g., "ALC")
            - startDate: Departure date (YYYY-MM-DD)
            - nights: Number of nights for return
            - adults: Number of adult passengers
            - children: Number of child passengers
            - cabin: Cabin class (economy, premium_economy, business, first)
    
    Returns:
        List of normalized flight dictionaries
    """
    api_key = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_KEY")
    if not api_key:
        print("[ERROR] Missing RAPIDAPI_GOOGLE_FLIGHTS_KEY")
        return []
    
    # Calculate return date
    departure_date = datetime.strptime(params["startDate"], "%Y-%m-%d")
    return_date = departure_date + timedelta(days=params["nights"])
    
    # Prepare search parameters
    search_params = {
        "from": params["origin"],
        "to": params["destination"],
        "date": params["startDate"],
        "returnDate": return_date.strftime("%Y-%m-%d"),
        "adults": params.get("adults", 1),
        "children": params.get("children", 0),
        "cabin": params.get("cabin", "economy"),
        "currency": "GBP"
    }
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": HOST
    }
    
    try:
        print(f"[INFO] Searching Google Flights: {params['origin']} → {params['destination']}")
        response = requests.get(
            f"{BASE_URL}/search",
            headers=headers,
            params=search_params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        flights = data.get("flights", [])
        
        if not flights:
            print("[INFO] No Google Flights results found")
            return []
        
        # Normalize and filter results
        normalized_flights = []
        for flight in flights:
            normalized = _normalize_flight_data(flight)
            if normalized and normalized.get("price", 0) > 0:
                normalized_flights.append(normalized)
        
        print(f"[INFO] Found {len(normalized_flights)} Google Flights options")
        return normalized_flights
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Google Flights API request failed: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error in Google Flights search: {e}")
        return []



