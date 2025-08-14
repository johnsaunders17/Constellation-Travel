import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# RapidAPI Booking.com Flights configuration
HOST = os.getenv("RAPIDAPI_BOOKING_HOST", "booking-com18.p.rapidapi.com")
BASE_URL = f"https://{HOST}"

def _normalize_flight_data(flight_data: dict) -> dict:
    """Normalize Booking.com flight data to match our standard format"""
    try:
        # Extract price information from travelerPrices
        traveler_prices = flight_data.get("travelerPrices", [])
        if traveler_prices and len(traveler_prices) > 0:
            price_info = traveler_prices[0].get("price", {})
            price = price_info.get("price", {}).get("value", 0) if isinstance(price_info.get("price"), dict) else 0
        else:
            price = 0
        
        # Extract airline information from the first segment
        bounds = flight_data.get("bounds", [])
        if bounds and len(bounds) > 0:
            segments = bounds[0].get("segments", [])
            if segments and len(segments) > 0:
                first_segment = segments[0]
                airline = first_segment.get("marketingCarrier", {}).get("name", "Unknown")
                flight_number = first_segment.get("flightNumber", "")
                carrier = f"{airline} {flight_number}".strip()
            else:
                carrier = "Unknown"
        else:
            carrier = "Unknown"
        
        # Extract departure and arrival times from bounds
        departure_time = ""
        arrival_time = ""
        if bounds and len(bounds) > 0:
            outbound = bounds[0]
            segments = outbound.get("segments", [])
            if segments:
                first_segment = segments[0]
                departure_time = first_segment.get("departuredAt", "")
                last_segment = segments[-1]
                arrival_time = last_segment.get("arrivedAt", "")
        
        # Extract duration from bounds
        duration = ""
        if bounds and len(bounds) > 0:
            outbound = bounds[0]
            segments = outbound.get("segments", [])
            if segments:
                total_duration = sum(seg.get("duration", 0) for seg in segments if seg.get("duration"))
                duration = f"{total_duration // 60000} min" if total_duration else ""
        
        # Extract stops from bounds
        stops = 0
        if bounds and len(bounds) > 0:
            outbound = bounds[0]
            segments = outbound.get("segments", [])
            if segments:
                stops = len(segments) - 1
        
        # Extract booking link
        link = flight_data.get("shareableUrl", "")
        
        return {
            "provider": "Booking.com Flights via RapidAPI",
            "price": float(price) / 100 if price else 0.0,  # Convert from cents to dollars
            "carrier": carrier,
            "departure": departure_time,
            "arrival": arrival_time,
            "link": link,
            "duration": duration,
            "stops": stops
        }
    except Exception as e:
        print(f"[ERROR] Failed to normalize Booking.com flight data: {e}")
        return {}

def search_booking_flights(params: dict) -> list[dict]:
    """Search for flights using Booking.com API via RapidAPI"""
    try:
        api_key = os.getenv("RAPIDAPI_BOOKING_KEY")
        if not api_key:
            print("[ERROR] Missing RAPIDAPI_BOOKING_KEY")
            return []
        
        # Calculate return date if needed
        start_date = datetime.strptime(params["startDate"], "%Y-%m-%d")
        nights = params.get("nights", 1)
        return_date = start_date + timedelta(days=nights)
        
        # Headers
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": HOST,
        }
        
        # Determine if this is a round trip or one-way
        if nights > 1:
            # Round trip
            endpoint = "/flights/search-return"
            search_params = {
                "fromId": params["origin"],
                "toId": params["destination"],
                "departureDate": params["startDate"],
                "returnDate": return_date.strftime("%Y-%m-%d"),
                "cabinClass": params.get("cabin", "ECONOMY").upper()
                # Removed numberOfStops filter to get more results
            }
        else:
            # One-way
            endpoint = "/flights/search-oneway"
            search_params = {
                "fromId": params["origin"],
                "toId": params["destination"],
                "departureDate": params["startDate"],
                "cabinClass": params.get("cabin", "ECONOMY").upper()
                # Removed numberOfStops filter to get more results
            }
        
        print(f"[INFO] Searching Booking.com flights: {params['origin']} → {params['destination']}")
        
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            params=search_params,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Booking.com flights API request failed: {response.status_code} {response.reason} for url: {response.url}")
            return []
        
        data = response.json()
        
        # Extract flights from the correct response structure
        flights = data.get("data", {}).get("sponsoredTrips", []) or []
        
        if not flights:
            print("[INFO] No Booking.com flight results found")
            return []
        
        # Normalize and filter results
        normalized_flights = []
        for flight in flights:
            normalized = _normalize_flight_data(flight)
            if normalized and normalized.get("price", 0) > 0:
                normalized_flights.append(normalized)
        
        print(f"[INFO] Found {len(normalized_flights)} Booking.com flight options")
        return normalized_flights
        
    except Exception as e:
        print(f"[ERROR] Booking.com flights search failed: {e}")
        return []
