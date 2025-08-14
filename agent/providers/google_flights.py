import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# RapidAPI Google Flights configuration
HOST = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_HOST", "google-flights2.p.rapidapi.com")
BASE_URL = f"https://{HOST}"

def _normalize_flight_data(flight_data: dict) -> dict:
    """Normalize Google Flights data to match our standard format"""
    try:
        # Extract price information
        price = flight_data.get("price", 0)
        
        # Extract airline information from the first flight segment
        flights = flight_data.get("flights", [])
        if flights and len(flights) > 0:
            first_flight = flights[0]
            airline = first_flight.get("airline", "Unknown")
            flight_number = first_flight.get("flight_number", "")
            carrier = f"{airline} {flight_number}".strip()
        else:
            carrier = "Unknown"
        
        # Extract departure and arrival times
        departure_time = flight_data.get("departure_time", "")
        arrival_time = flight_data.get("arrival_time", "")
        
        # Extract duration
        duration_info = flight_data.get("duration", {})
        duration = duration_info.get("text", "") if isinstance(duration_info, dict) else str(duration_info)
        
        # Extract stops
        stops = flight_data.get("stops", 0)
        
        # Extract booking token
        booking_token = flight_data.get("booking_token", "")
        
        return {
            "provider": "Google Flights via RapidAPI",
            "price": float(price) if price else 0.0,
            "carrier": carrier,
            "departure": departure_time,
            "arrival": arrival_time,
            "link": f"https://www.google.com/travel/flights?token={booking_token}" if booking_token else "",
            "duration": duration,
            "stops": stops
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
        "departure_id": params["origin"],
        "arrival_id": params["destination"],
        "outbound_date": params["startDate"],
        "travel_class": params.get("cabin", "ECONOMY").upper(),
        "adults": params.get("adults", 1),
        "currency": "GBP",
        "language_code": "en-GB",
        "country_code": "GB",
        "search_type": "best"
    }
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": HOST
    }
    
    try:
        print(f"[INFO] Searching Google Flights: {params['origin']} → {params['destination']}")
        response = requests.get(
            f"{BASE_URL}/api/v1/searchFlights",
            headers=headers,
            params=search_params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Extract flights from the new response structure
        itineraries = data.get("data", {}).get("itineraries", {})
        top_flights = itineraries.get("topFlights", [])
        other_flights = itineraries.get("otherFlights", [])
        
        # Combine all flights
        all_flights = top_flights + other_flights
        
        if not all_flights:
            print("[INFO] No Google Flights results found")
            return []
        
        # Normalize and filter results
        normalized_flights = []
        for flight in all_flights:
            try:
                normalized = _normalize_flight_data(flight)
                if normalized and normalized.get("price", 0) > 0:
                    normalized_flights.append(normalized)
            except Exception as e:
                print(f"[WARN] Failed to normalize flight: {e}")
                continue
        
        print(f"[INFO] Found {len(normalized_flights)} Google Flights options")
        return normalized_flights
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Google Flights API request failed: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error in Google Flights search: {e}")
        return []



