import os
import json
import argparse
from datetime import datetime
import requests
from providers.kiwi import get_kiwi_deals
from providers.amadeus import get_amadeus_hotels
from providers.google_flights import search_google_flights
from providers.booking_com import search_booking_hotels

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_results(data, output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    output_file = f"{output_dir}/results-{timestamp}.json"
    latest_file = f"{output_dir}/latest.json"

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    with open(latest_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[INFO] Results saved to {output_file} and latest.json")

def evaluate_deals(params):
    # --- FLIGHTS ---
    ### Multi-provider flight search with fallbacks
    print("[INFO] Fetching flight data from multiple providers...")
    all_flights = []
    
    # Try Google Flights first (often has good deals)
    try:
        google_flights = search_google_flights(params) or []
        all_flights.extend(google_flights)
        print(f"[INFO] Google Flights: {len(google_flights)} options")
    except Exception as e:
        print(f"[ERROR] Google Flights failed: {e}")
    
    # Try Booking.com Flights
    try:
        from providers.booking_com_flights import search_booking_flights
        booking_flights = search_booking_flights(params) or []
        all_flights.extend(booking_flights)
        print(f"[INFO] Booking.com Flights: {len(booking_flights)} options")
    except Exception as e:
        print(f"[ERROR] Booking.com Flights failed: {e}")
    
    # Try Amadeus Flights
    try:
        from providers.amadeus_flights import search_roundtrip as get_amadeus_flights
        amadeus_flights = get_amadeus_flights(params) or []
        all_flights.extend(amadeus_flights)
        print(f"[INFO] Amadeus Flights: {len(amadeus_flights)} options")
    except Exception as e:
        print(f"[ERROR] Amadeus Flights failed: {e}")
    
    # Fallback to Kiwi if needed
    if not all_flights:
        print("[WARN] No primary flight results, trying Kiwi...")
        try:
            kiwi_flights = get_kiwi_deals(params) or []
            all_flights.extend(kiwi_flights)
            print(f"[INFO] Kiwi: {len(kiwi_flights)} options")
        except Exception as e:
            print(f"[ERROR] Kiwi provider failed: {e}")
    
    # Remove duplicates and sort by price
    unique_flights = []
    seen_prices = set()
    for flight in sorted(all_flights, key=lambda x: x.get("price", 0)):
        price_key = f"{flight.get('carrier', '')}-{flight.get('price', 0)}-{flight.get('departure', '')}"
        if price_key not in seen_prices:
            unique_flights.append(flight)
            seen_prices.add(price_key)
    
    print(f"[INFO] Total unique flights found: {len(unique_flights)}")

    # --- HOTELS ---
    ### Multi-provider hotel search
    print("[INFO] Fetching hotel data from multiple providers...")
    all_hotels = []
    
    # Try Booking.com first (often has competitive rates)
    try:
        booking_hotels = search_booking_hotels(params) or []
        all_hotels.extend(booking_hotels)
        print(f"[INFO] Booking.com: {len(booking_hotels)} options")
    except Exception as e:
        print(f"[ERROR] Booking.com failed: {e}")
    
    # Try Amadeus Hotels
    try:
        amadeus_hotels = get_amadeus_hotels(params) or []
        all_hotels.extend(amadeus_hotels)
        print(f"[INFO] Amadeus Hotels: {len(amadeus_hotels)} options")
    except Exception as e:
        print(f"[ERROR] Amadeus Hotels failed: {e}")
    
    # Remove duplicates and sort by price
    unique_hotels = []
    seen_hotel_keys = set()
    for hotel in sorted(all_hotels, key=lambda x: x.get("price", 0)):
        hotel_key = f"{hotel.get('name', '')}-{hotel.get('stars', 0)}-{hotel.get('board', '')}"
        if hotel_key not in seen_hotel_keys:
            unique_hotels.append(hotel)
            seen_hotel_keys.add(hotel_key)
    
    print(f"[INFO] Total unique hotels found: {len(unique_hotels)}")

    # --- MATCH & FILTER ---
    results = []
    for flight in unique_flights:
        for hotel in unique_hotels:
            if hotel["stars"] >= params["minStars"] and params["board"].lower() in hotel["board"].lower():
                total = float(flight["price"]) + float(hotel["price"])
                per_person = total / params["adults"]
                if per_person <= params["budgetPerPerson"]:
                    results.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "perPerson": round(per_person, 2),
                        "total": round(total, 2),
                        "flight": flight,
                        "hotel": hotel
                    })

    sorted_results = sorted(results, key=lambda x: x["perPerson"])
    print(f"[INFO] {len(sorted_results)} matching deals found.")
    return sorted_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/request.json", help="Path to config JSON")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"[ERROR] Config file not found at {args.config}")
        exit(1)

    config = load_config(args.config)
    try:
        deals = evaluate_deals(config)
        output = {"deals": deals, "count": len(deals), "queriedAt": datetime.utcnow().isoformat()}
        save_results(output)
    except Exception as e:
        print(f"[ERROR] Agent failed: {e}")
        exit(1)
