#!/usr/bin/env python3
"""
Test script to find the correct API endpoints for Google Flights and Booking.com
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_flights_endpoints():
    """Test different Google Flights API endpoints"""
    print("🔍 Testing Google Flights API endpoints...")
    
    api_key = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_KEY")
    host = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_HOST")
    
    if not api_key:
        print("❌ RAPIDAPI_GOOGLE_FLIGHTS_KEY not set")
        return
    
    print(f"Using host: {host}")
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }
    
    # Test different endpoints
    endpoints = [
        "/search",
        "/v1/search",
        "/flights/search",
        "/api/search",
        "/"
    ]
    
    for endpoint in endpoints:
        url = f"https://{host}{endpoint}"
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success! This endpoint works")
                print(f"Response: {response.text[:200]}...")
                return endpoint
            elif response.status_code == 404:
                print("❌ Not Found")
            elif response.status_code == 403:
                print("❌ Forbidden (might be wrong endpoint)")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

def test_booking_com_endpoints():
    """Test different Booking.com API endpoints"""
    print("\n🔍 Testing Booking.com API endpoints...")
    
    api_key = os.getenv("RAPIDAPI_BOOKING_KEY")
    host = os.getenv("RAPIDAPI_BOOKING_HOST")
    
    if not api_key:
        print("❌ RAPIDAPI_BOOKING_KEY not set")
        return
    
    print(f"Using host: {host}")
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }
    
    # Test different endpoints
    endpoints = [
        "/v1/hotels/search",
        "/hotels/search",
        "/search",
        "/v1/search",
        "/api/hotels",
        "/"
    ]
    
    for endpoint in endpoints:
        url = f"https://{host}{endpoint}"
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success! This endpoint works")
                print(f"Response: {response.text[:200]}...")
                return endpoint
            elif response.status_code == 404:
                print("❌ Not Found")
            elif response.status_code == 403:
                print("❌ Forbidden (might be wrong endpoint)")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

def test_api_info():
    """Test getting API information"""
    print("\n🔍 Testing API information endpoints...")
    
    # Test Google Flights
    api_key = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_KEY")
    host = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_HOST")
    
    if api_key and host:
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": host
        }
        
        # Try to get API info
        try:
            url = f"https://{host}/"
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Google Flights root endpoint: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text[:300]}...")
        except Exception as e:
            print(f"Google Flights error: {e}")
    
    # Test Booking.com
    api_key = os.getenv("RAPIDAPI_BOOKING_KEY")
    host = os.getenv("RAPIDAPI_BOOKING_HOST")
    
    if api_key and host:
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": host
        }
        
        # Try to get API info
        try:
            url = f"https://{host}/"
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Booking.com root endpoint: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text[:300]}...")
        except Exception as e:
            print(f"Booking.com error: {e}")

def main():
    """Run all tests"""
    print("🚀 API Endpoint Discovery Tool")
    print("=" * 40)
    
    # Test endpoints
    google_endpoint = test_google_flights_endpoints()
    booking_endpoint = test_booking_com_endpoints()
    
    # Test API info
    test_api_info()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Summary:")
    if google_endpoint:
        print(f"✅ Google Flights: {google_endpoint}")
    else:
        print("❌ Google Flights: No working endpoint found")
    
    if booking_endpoint:
        print(f"✅ Booking.com: {booking_endpoint}")
    else:
        print("❌ Booking.com: No working endpoint found")
    
    if not google_endpoint and not booking_endpoint:
        print("\n💡 Next steps:")
        print("1. Check your RapidAPI dashboard for the correct endpoints")
        print("2. Verify the API subscription is active")
        print("3. Check the API documentation for the correct paths")

if __name__ == "__main__":
    main()
