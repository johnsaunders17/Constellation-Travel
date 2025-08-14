#!/usr/bin/env python3
"""
Smoke test for Google Flights provider via RapidAPI
Tests the API integration and data normalization
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the providers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from providers.google_flights import search_google_flights, _normalize_flight_data

def test_normalize_flight_data():
    """Test the flight data normalization function"""
    print("🧪 Testing flight data normalization...")
    
    # Test case 1: Standard flight data
    test_flight = {
        "price": {"amount": 150.50, "currency": "GBP"},
        "airline": "British Airways",
        "route": {
            "departure": "2025-08-25T10:00:00",
            "arrival": "2025-08-25T13:00:00"
        },
        "duration": "3h",
        "stops": 0
    }
    
    normalized = _normalize_flight_data(test_flight)
    assert normalized["price"] == 150.50, f"Expected price 150.50, got {normalized['price']}"
    assert normalized["carrier"] == "British Airways", f"Expected carrier 'British Airways', got {normalized['carrier']}"
    assert normalized["provider"] == "Google Flights via RapidAPI", f"Expected provider 'Google Flights via RapidAPI', got {normalized['provider']}"
    
    print("✅ Flight data normalization test passed")
    
    # Test case 2: Missing data handling
    incomplete_flight = {
        "price": None,
        "airline": None,
        "route": {}
    }
    
    normalized = _normalize_flight_data(incomplete_flight)
    assert normalized["price"] == 0.0, f"Expected price 0.0 for missing data, got {normalized['price']}"
    assert normalized["carrier"] == "Unknown", f"Expected carrier 'Unknown' for missing data, got {normalized['carrier']}"
    
    print("✅ Incomplete data handling test passed")

def test_google_flights_search():
    """Test the Google Flights search function"""
    print("🧪 Testing Google Flights search...")
    
    # Check if API key is available
    api_key = os.getenv("RAPIDAPI_GOOGLE_FLIGHTS_KEY")
    if not api_key:
        print("⚠️  RAPIDAPI_GOOGLE_FLIGHTS_KEY not set, skipping live API test")
        print("   Set the environment variable to test the live API")
        return
    
    # Test search parameters
    test_params = {
        "origin": "EMA",
        "destination": "ALC",
        "startDate": "2025-08-25",
        "nights": 4,
        "adults": 2,
        "children": 0,
        "cabin": "economy"
    }
    
    try:
        print(f"🔍 Searching for flights: {test_params['origin']} → {test_params['destination']}")
        results = search_google_flights(test_params)
        
        if results:
            print(f"✅ Found {len(results)} flight options")
            
            # Validate first result structure
            first_result = results[0]
            required_fields = ["provider", "price", "carrier", "departure", "arrival"]
            for field in required_fields:
                assert field in first_result, f"Missing required field: {field}"
            
            print("✅ Result structure validation passed")
            
            # Print sample result
            print(f"📋 Sample result: {json.dumps(first_result, indent=2)}")
            
        else:
            print("ℹ️  No flight results found (this might be normal for the test route)")
            
    except Exception as e:
        print(f"❌ Google Flights search failed: {e}")
        raise

def test_error_handling():
    """Test error handling scenarios"""
    print("🧪 Testing error handling...")
    
    # Test with missing API key
    original_key = os.environ.get("RAPIDAPI_GOOGLE_FLIGHTS_KEY")
    if original_key:
        del os.environ["RAPIDAPI_GOOGLE_FLIGHTS_KEY"]
    
    try:
        results = search_google_flights({"origin": "EMA", "destination": "ALC", "startDate": "2025-08-25", "nights": 4})
        assert results == [], "Expected empty results when API key is missing"
        print("✅ Missing API key handling test passed")
    finally:
        # Restore original key if it existed
        if original_key:
            os.environ["RAPIDAPI_GOOGLE_FLIGHTS_KEY"] = original_key
    
    # Test with invalid parameters
    try:
        results = search_google_flights({"invalid": "params", "startDate": "2025-08-25", "nights": 4, "origin": "EMA", "destination": "ALC"})
        # Should handle gracefully without crashing
        print("✅ Invalid parameters handling test passed")
    except Exception as e:
        print(f"❌ Invalid parameters handling failed: {e}")
        raise

def main():
    """Run all smoke tests"""
    print("🚀 Starting Google Flights Provider Smoke Tests")
    print("=" * 50)
    
    try:
        test_normalize_flight_data()
        test_error_handling()
        test_google_flights_search()
        
        print("\n🎉 All Google Flights smoke tests passed!")
        return 0
        
    except Exception as e:
        print(f"\n💥 Smoke test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())



