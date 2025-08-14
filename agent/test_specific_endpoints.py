#!/usr/bin/env python3
"""
Test specific API endpoints that seem to exist
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_flights_v1_search():
    """Test the Google Flights v1/search endpoint with proper parameters"""
    print("🔍 Testing Google Flights v1/search endpoint...")
    
    api_key = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_KEY")
    host = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_HOST")
    
    if not api_key:
        print("❌ RAPIDAPI_GOOGLE_FLIGHTS_KEY not set")
        return False
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }
    
    # Test with minimal parameters
    url = f"https://{host}/v1/search"
    
    # Try different parameter combinations
    test_params = [
        {"from": "LHR", "to": "JFK", "date": "2025-01-15"},
        {"origin": "LHR", "destination": "JFK", "date": "2025-01-15"},
        {"departure": "LHR", "arrival": "JFK", "date": "2025-01-15"},
        {"from": "LHR", "to": "JFK", "departure_date": "2025-01-15"},
    ]
    
    for i, params in enumerate(test_params, 1):
        try:
            print(f"\nTest {i}: {params}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success! Found working parameters")
                print(f"Response: {response.text[:300]}...")
                return True
            elif response.status_code == 429:
                print("⚠️  Rate limited - this endpoint exists but we're hitting limits")
                return True
            elif response.status_code == 400:
                print("⚠️  Bad Request - endpoint exists but wrong parameters")
            elif response.status_code == 404:
                print("❌ Not Found")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def test_booking_com_hotels_search():
    """Test the Booking.com hotels search endpoint with proper parameters"""
    print("\n🔍 Testing Booking.com hotels search endpoint...")
    
    api_key = os.getenv("RAPIDAPI_BOOKING_KEY")
    host = os.getenv("RAPIDAPI_BOOKING_HOST")
    
    if not api_key:
        print("❌ RAPIDAPI_BOOKING_KEY not set")
        return False
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }
    
    # Test with minimal parameters
    url = f"https://{host}/v1/hotels/search"
    
    # Try different parameter combinations
    test_params = [
        {"dest_id": "LON", "arrival_date": "2025-01-15", "departure_date": "2025-01-20"},
        {"destination": "LON", "check_in": "2025-01-15", "check_out": "2025-01-20"},
        {"city": "LON", "arrival": "2025-01-15", "departure": "2025-01-20"},
        {"location": "LON", "arrival_date": "2025-01-15", "departure_date": "2025-01-20"},
    ]
    
    for i, params in enumerate(test_params, 1):
        try:
            print(f"\nTest {i}: {params}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success! Found working parameters")
                print(f"Response: {response.text[:300]}...")
                return True
            elif response.status_code == 429:
                print("⚠️  Rate limited - this endpoint exists but we're hitting limits")
                return True
            elif response.status_code == 400:
                print("⚠️  Bad Request - endpoint exists but wrong parameters")
            elif response.status_code == 403:
                print("⚠️  Forbidden - endpoint exists but needs different auth/params")
            elif response.status_code == 404:
                print("❌ Not Found")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def main():
    """Run targeted tests"""
    print("🚀 Targeted API Endpoint Testing")
    print("=" * 40)
    
    # Test Google Flights
    google_working = test_google_flights_v1_search()
    
    # Test Booking.com
    booking_working = test_booking_com_hotels_search()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Summary:")
    
    if google_working:
        print("✅ Google Flights: Endpoint found and working")
    else:
        print("❌ Google Flights: Endpoint not working")
    
    if booking_working:
        print("✅ Booking.com: Endpoint found and working")
    else:
        print("❌ Booking.com: Endpoint not working")
    
    if google_working or booking_working:
        print("\n🎉 Progress! At least one API is working.")
        print("The 429 errors mean you're hitting rate limits, which is normal.")
        print("Try again later or check your RapidAPI usage limits.")
    else:
        print("\n💡 Next steps:")
        print("1. Check your RapidAPI dashboard for the exact API names")
        print("2. Look at the API documentation for the correct endpoints")
        print("3. Verify your subscription is active")

if __name__ == "__main__":
    main()
