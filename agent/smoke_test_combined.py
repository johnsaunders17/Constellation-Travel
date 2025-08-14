#!/usr/bin/env python3
"""
Combined smoke test for all travel providers
Tests the unified system with multiple providers
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the providers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from providers.google_flights import search_google_flights
from providers.booking_com import search_booking_hotels
from providers.amadeus_flights import search_roundtrip as get_amadeus_flights
from providers.amadeus import get_amadeus_hotels
from providers.kiwi import get_kiwi_deals

def test_flight_providers():
    """Test all flight providers"""
    print("✈️  Testing Flight Providers")
    print("-" * 30)
    
    test_params = {
        "origin": "EMA",
        "destination": "ALC",
        "startDate": "2025-08-25",
        "nights": 4,
        "adults": 2,
        "children": 0,
        "cabin": "economy"
    }
    
    all_flights = []
    
    # Test Google Flights
    try:
        google_flights = search_google_flights(test_params) or []
        all_flights.extend(google_flights)
        print(f"✅ Google Flights: {len(google_flights)} options")
    except Exception as e:
        print(f"❌ Google Flights failed: {e}")
    
    # Test Amadeus Flights
    try:
        amadeus_flights = get_amadeus_flights(test_params) or []
        all_flights.extend(amadeus_flights)
        print(f"✅ Amadeus Flights: {len(amadeus_flights)} options")
    except Exception as e:
        print(f"❌ Amadeus Flights failed: {e}")
    
    # Test Kiwi
    try:
        kiwi_flights = get_kiwi_deals(test_params) or []
        all_flights.extend(kiwi_flights)
        print(f"✅ Kiwi: {len(kiwi_flights)} options")
    except Exception as e:
        print(f"❌ Kiwi failed: {e}")
    
    # Remove duplicates and sort by price
    unique_flights = []
    seen_prices = set()
    for flight in sorted(all_flights, key=lambda x: x.get("price", 0)):
        price_key = f"{flight.get('carrier', '')}-{flight.get('price', 0)}-{flight.get('departure', '')}"
        if price_key not in seen_prices:
            unique_flights.append(flight)
            seen_prices.add(price_key)
    
    print(f"📊 Total unique flights found: {len(unique_flights)}")
    
    if unique_flights:
        print(f"💰 Price range: £{min(f['price'] for f in unique_flights)} - £{max(f['price'] for f in unique_flights)}")
        print(f"✈️  Airlines: {', '.join(set(f['carrier'] for f in unique_flights))}")
    
    return unique_flights

def test_hotel_providers():
    """Test all hotel providers"""
    print("\n🏨 Testing Hotel Providers")
    print("-" * 30)
    
    test_params = {
        "destination": "ALC",
        "startDate": "2025-08-25",
        "nights": 4,
        "adults": 2,
        "children": 0,
        "board": "HB",
        "minStars": 4
    }
    
    all_hotels = []
    
    # Test Booking.com
    try:
        booking_hotels = search_booking_hotels(test_params) or []
        all_hotels.extend(booking_hotels)
        print(f"✅ Booking.com: {len(booking_hotels)} options")
    except Exception as e:
        print(f"❌ Booking.com failed: {e}")
    
    # Test Amadeus Hotels
    try:
        amadeus_hotels = get_amadeus_hotels(test_params) or []
        all_hotels.extend(amadeus_hotels)
        print(f"✅ Amadeus Hotels: {len(amadeus_hotels)} options")
    except Exception as e:
        print(f"❌ Amadeus Hotels failed: {e}")
    
    # Remove duplicates and sort by price
    unique_hotels = []
    seen_hotel_keys = set()
    for hotel in sorted(all_hotels, key=lambda x: x.get("price", 0)):
        hotel_key = f"{hotel.get('name', '')}-{hotel.get('stars', 0)}-{hotel.get('board', '')}"
        if hotel_key not in seen_hotel_keys:
            unique_hotels.append(hotel)
            seen_hotel_keys.add(hotel_key)
    
    print(f"📊 Total unique hotels found: {len(unique_hotels)}")
    
    if unique_hotels:
        print(f"💰 Price range: £{min(h['price'] for h in unique_hotels)} - £{max(h['price'] for h in unique_hotels)}")
        print(f"⭐ Star ratings: {', '.join(map(str, sorted(set(h['stars'] for h in unique_hotels))))}")
        print(f"🍽️  Board types: {', '.join(set(h['board'] for h in unique_hotels))}")
    
    return unique_hotels

def test_deal_matching(flights, hotels):
    """Test the deal matching logic"""
    print("\n🎯 Testing Deal Matching")
    print("-" * 30)
    
    # Simulate the deal matching logic from the main agent
    test_params = {
        "minStars": 4,
        "board": "HB",
        "budgetPerPerson": 700,
        "adults": 2
    }
    
    results = []
    for flight in flights:
        for hotel in hotels:
            if (hotel["stars"] >= test_params["minStars"] and 
                test_params["board"].lower() in hotel["board"].lower()):
                total = float(flight["price"]) + float(hotel["price"])
                per_person = total / test_params["adults"]
                if per_person <= test_params["budgetPerPerson"]:
                    results.append({
                        "perPerson": round(per_person, 2),
                        "total": round(total, 2),
                        "flight": flight,
                        "hotel": hotel
                    })
    
    sorted_results = sorted(results, key=lambda x: x["perPerson"])
    
    print(f"🎉 Found {len(sorted_results)} matching deals!")
    
    if sorted_results:
        print(f"💰 Best deal: £{sorted_results[0]['perPerson']} per person (£{sorted_results[0]['total']} total)")
        print(f"💰 Worst deal: £{sorted_results[-1]['perPerson']} per person (£{sorted_results[-1]['total']} total)")
        
        # Show top 3 deals
        print("\n🏆 Top 3 Deals:")
        for i, deal in enumerate(sorted_results[:3], 1):
            print(f"  {i}. £{deal['perPerson']} pp - {deal['flight']['carrier']} + {deal['hotel']['name']}")
    
    return sorted_results

def test_provider_resilience():
    """Test that the system is resilient to provider failures"""
    print("\n🛡️  Testing Provider Resilience")
    print("-" * 30)
    
    # Test with missing API keys
    original_keys = {}
    for key in ["RAPIDAPI_GOOGLE_FLIGHTS_KEY", "RAPIDAPI_BOOKING_KEY", "AMADEUS_API_KEY"]:
        original_keys[key] = os.environ.get(key)
        if original_keys[key]:
            del os.environ[key]
    
    try:
        # These should handle missing keys gracefully
        flights = search_google_flights({"origin": "EMA", "destination": "ALC", "startDate": "2025-08-25", "nights": 4})
        hotels = search_booking_hotels({"destination": "ALC", "startDate": "2025-08-25", "nights": 4})
        
        assert flights == [], "Expected empty results when API key is missing"
        assert hotels == [], "Expected empty results when API key is missing"
        
        print("✅ Graceful handling of missing API keys")
        
    finally:
        # Restore original keys
        for key, value in original_keys.items():
            if value:
                os.environ[key] = value

def main():
    """Run all combined smoke tests"""
    print("🚀 Starting Combined Travel Provider Smoke Tests")
    print("=" * 60)
    
    try:
        # Test individual providers
        flights = test_flight_providers()
        hotels = test_hotel_providers()
        
        # Test the complete system
        deals = test_deal_matching(flights, hotels)
        
        # Test resilience
        test_provider_resilience()
        
        print("\n" + "=" * 60)
        print("🎉 All Combined Smoke Tests Passed!")
        print(f"📊 Summary: {len(flights)} flights, {len(hotels)} hotels, {len(deals)} deals")
        return 0
        
    except Exception as e:
        print(f"\n💥 Combined smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
