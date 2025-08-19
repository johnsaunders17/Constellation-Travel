# Configuration for Constellation Travel API
import os

# RapidAPI Configuration
# Get your API key from: https://rapidapi.com/
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'your-rapidapi-key-here')

# API Hosts
RAPIDAPI_HOSTS = {
    'google_flights': 'google-flights2.p.rapidapi.com',
    'booking_com': 'booking-com15.p.rapidapi.com',
    'booking_com_flights': 'booking-com18.p.rapidapi.com',
    'booking_com_tipsters': 'tipsters.p.rapidapi.com',  # NEW: Tipsters Booking.com API
    'flights_sky': 'flights-sky.p.rapidapi.com'
}

# Individual API Keys (if needed)
RAPIDAPI_FLIGHTS_SKY_KEY = os.getenv('RAPIDAPI_SKYSCRAPER_KEY', RAPIDAPI_KEY)
RAPIDAPI_BOOKING_TIPSTERS_KEY = os.getenv('RAPIDAPI_BOOKING_KEY', RAPIDAPI_KEY)  # NEW

# Default settings
DEFAULT_CURRENCY = 'GBP'
DEFAULT_LANGUAGE = 'en-GB'
DEFAULT_COUNTRY = 'GB'

# Flight search defaults
DEFAULT_TRAVEL_CLASS = 'ECONOMY'
DEFAULT_ADULTS = 1
DEFAULT_CHILDREN = 0
DEFAULT_SENIORS = 0
