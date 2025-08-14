#!/usr/bin/env python3
"""
Smoke test for Booking.com provider via RapidAPI
Tests the API integration and data normalization
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the providers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from providers.booking_com import search_booking_hotels, _normalize_hotel_data

def test_normalize_hotel_data():
    """Test the hotel data normalization function"""
    print("🧪 Testing hotel data normalization...")
    
    # Test case 1: Standard hotel data
    test_hotel = {
        "hotel": {
            "name": "Test Hotel",
            "rating": 4.5,
            "address": {"city": "Alicante"}
        },
        "price": {"amount": 120.00, "currency": "GBP"},
        "board": "Half Board",
        "amenities": ["WiFi", "Pool", "Spa"]
    }
    
    normalized = _normalize_hotel_data(test_hotel)
    assert normalized["name"] == "Test Hotel", f"Expected name 'Test Hotel', got {normalized['name']}"
    assert normalized["price"] == 120.00, f"Expected price 120.00, got {normalized['price']}"
    assert normalized["stars"] == 4, f"Expected stars 4, got {normalized['stars']}"
    assert normalized["board"] == "Half Board", f"Expected board 'Half Board', got {normalized['board']}"
    assert normalized["provider"] == "Booking.com via RapidAPI", f"Expected provider 'Booking.com via RapidAPI', got {normalized['provider']}"
    
    print("✅ Hotel data normalization test passed")
    
    # Test case 2: Missing data handling
    incomplete_hotel = {
        "hotel": {},
        "price": None,
        "board": None
    }
    
    normalized = _normalize_hotel_data(incomplete_hotel)
    assert normalized["name"] == "Unknown Hotel", f"Expected name 'Unknown Hotel' for missing data, got {normalized['name']}"
    assert normalized["price"] == 0.0, f"Expected price 0.0 for missing data, got {normalized['price']}"
    assert normalized["stars"] == 3, f"Expected stars 3 for missing data, got {normalized['stars']}"
    
    print("✅ Incomplete data handling test passed")

def test_booking_hotels_search():
    """Test the Booking.com hotels search function"""
    print("🧪 Testing Booking.com hotels search...")
    
    # Check if API key is available
    api_key = os.getenv("RAPIDAPI_BOOKING_KEY")
    if not api_key:
        print("⚠️  RAPIDAPI_BOOKING_KEY not set, skipping live API test")
        print("   Set the environment variable to test the live API")
        return
    
    # Test search parameters
    test_params = {
        "destination": "ALC",
        "startDate": "2025-08-25",
        "nights": 4,
        "adults": 2,
        "children": 0,
        "board": "HB",
        "minStars": 4
    }
    
    try:
        print(f"🔍 Searching for hotels in {test_params['destination']}")
        results = search_booking_hotels(test_params)
        
        if results:
            print(f"✅ Found {len(results)} hotel options")
            
            # Validate first result structure
            first_result = results[0]
            required_fields = ["provider", "name", "stars", "rating", "board", "price"]
            for field in required_fields:
                assert field in first_result, f"Missing required field: {field}"
            
            print("✅ Result structure validation passed")
            
            # Print sample result
            print(f"📋 Sample result: {json.dumps(first_result, indent=2)}")
            
        else:
            print("ℹ️  No hotel results found (this might be normal for the test destination)")
            
    except Exception as e:
        print(f"❌ Booking.com hotels search failed: {e}")
        raise

def test_error_handling():
    """Test error handling scenarios"""
    print("🧪 Testing error handling...")
    
    # Test with missing API key
    original_key = os.environ.get("RAPIDAPI_BOOKING_KEY")
    if original_key:
        del os.environ["RAPIDAPI_BOOKING_KEY"]
    
    try:
        results = search_booking_hotels({"destination": "ALC", "startDate": "2025-08-25", "nights": 4})
        assert results == [], "Expected empty results when API key is missing"
        print("✅ Missing API key handling test passed")
    finally:
        # Restore original key if it existed
        if original_key:
            os.environ["RAPIDAPI_BOOKING_KEY"] = original_key
    
    # Test with invalid parameters
    try:
        results = search_booking_hotels({"invalid": "params"})
        # Should handle gracefully without crashing
        print("✅ Invalid parameters handling test passed")
    except Exception as e:
        print(f"❌ Invalid parameters handling failed: {e}")
        raise

def test_filtering():
    """Test the filtering logic"""
    print("🧪 Testing filtering logic...")
    
    # Test minimum stars filtering
    test_params = {"minStars": 4}
    
    # Mock hotel data with different star ratings
    mock_hotels = [
        {"hotel": {"name": "3 Star Hotel"}, "price": {"amount": 80}, "board": "RO"},
        {"hotel": {"name": "4 Star Hotel"}, "price": {"amount": 120}, "board": "HB"},
        {"hotel": {"name": "5 Star Hotel"}, "price": {"amount": 200}, "board": "FB"}
    ]
    
    # Simulate the filtering logic
    filtered_hotels = []
    for hotel in mock_hotels:
        normalized = _normalize_hotel_data(hotel)
        if (normalized and 
            normalized.get("price", 0) > 0 and 
            normalized.get("stars", 0) >= test_params.get("minStars", 3)):
            filtered_hotels.append(normalized)
    
    # Should only include 4 and 5 star hotels
    assert len(filtered_hotels) == 2, f"Expected 2 hotels after filtering, got {len(filtered_hotels)}"
    assert all(hotel["stars"] >= 4 for hotel in filtered_hotels), "All filtered hotels should be 4+ stars"
    
    print("✅ Filtering logic test passed")

def main():
    """Run all smoke tests"""
    print("🚀 Starting Booking.com Provider Smoke Tests")
    print("=" * 50)
    
    try:
        test_normalize_hotel_data()
        test_error_handling()
        test_filtering()
        test_booking_hotels_search()
        
        print("\n🎉 All Booking.com smoke tests passed!")
        return 0
        
    except Exception as e:
        print(f"\n💥 Smoke test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())



