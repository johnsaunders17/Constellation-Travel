import os
import requests
from datetime import datetime, timedelta

# RapidAPI Booking.com configuration
HOST = os.getenv("RAPIDAPI_BOOKING_HOST", "booking-com.p.rapidapi.com")
BASE_URL = f"https://{HOST}"

def _normalize_hotel_data(hotel_data: dict) -> dict:
    """Normalize Booking.com data to match our standard format"""
    try:
        # Extract price information
        price_info = hotel_data.get("price", {})
        if isinstance(price_info, dict):
            price = price_info.get("amount") or price_info.get("total") or price_info.get("current")
        else:
            price = price_info
        
        # Extract hotel information
        hotel_info = hotel_data.get("hotel", {})
        name = hotel_info.get("name") or hotel_data.get("name")
        
        # Extract rating/stars
        rating = hotel_info.get("rating") or hotel_data.get("rating", 3)
        stars = hotel_info.get("stars") or hotel_data.get("stars", 3)
        
        # Extract board type
        board = hotel_data.get("board") or hotel_data.get("mealPlan") or "Room Only"
        
        # Extract booking link
        link = hotel_data.get("bookingLink") or hotel_data.get("url") or ""
        
        return {
            "provider": "Booking.com via RapidAPI",
            "name": name or "Unknown Hotel",
            "stars": int(stars) if stars else 3,
            "rating": float(rating) if rating else 3.0,
            "board": board,
            "price": float(price) if price else 0.0,
            "link": link,
            "location": hotel_info.get("address", {}).get("city") or hotel_data.get("city"),
            "amenities": hotel_data.get("amenities", [])
        }
    except Exception as e:
        print(f"[ERROR] Failed to normalize Booking.com data: {e}")
        return {}

def search_booking_hotels(params: dict) -> list[dict]:
    """
    Search for hotels using Booking.com via RapidAPI
    
    Args:
        params: Dictionary containing search parameters
            - destination: Destination city or airport code
            - startDate: Check-in date (YYYY-MM-DD)
            - nights: Number of nights
            - adults: Number of adult guests
            - children: Number of child guests
            - board: Board type (e.g., "HB", "BB", "RO")
            - minStars: Minimum hotel star rating
    
    Returns:
        List of normalized hotel dictionaries
    """
    api_key = os.getenv("RAPIDAPI_BOOKING_KEY")
    if not api_key:
        print("[ERROR] Missing RAPIDAPI_BOOKING_KEY")
        return []
    
    # Calculate check-out date
    check_in = datetime.strptime(params["startDate"], "%Y-%m-%d")
    check_out = check_in + timedelta(days=params["nights"])
    
    # Prepare search parameters
    search_params = {
        "dest_id": params.get("destination", "ALC"),
        "search_type": "city",
        "arrival_date": params["startDate"],
        "departure_date": check_out.strftime("%Y-%m-%d"),
        "adults": params.get("adults", 1),
        "children": params.get("children", 0),
        "room_qty": 1,
        "currency": "GBP",
        "locale": "en-gb"
    }
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": HOST
    }
    
    try:
        print(f"[INFO] Searching Booking.com hotels in {params.get('destination', 'ALC')}")
        response = requests.get(
            f"{BASE_URL}/v1/hotels/search",
            headers=headers,
            params=search_params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        hotels = data.get("result", [])
        
        if not hotels:
            print("[INFO] No Booking.com hotel results found")
            return []
        
        # Normalize and filter results
        normalized_hotels = []
        min_stars = params.get("minStars", 3)
        
        for hotel in hotels:
            normalized = _normalize_hotel_data(hotel)
            if (normalized and 
                normalized.get("price", 0) > 0 and 
                normalized.get("stars", 0) >= min_stars):
                normalized_hotels.append(normalized)
        
        print(f"[INFO] Found {len(normalized_hotels)} Booking.com hotel options")
        return normalized_hotels
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Booking.com API request failed: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error in Booking.com search: {e}")
        return []



