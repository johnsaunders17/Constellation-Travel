from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import re
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Import configuration
try:
    from config import RAPIDAPI_KEY, RAPIDAPI_HOSTS
except ImportError:
    # Fallback for deployment environments
    import os
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'demo-key')
    RAPIDAPI_HOSTS = {
        'google_flights': 'google-flights2.p.rapidapi.com',
        'booking_com': 'booking-com15.p.rapidapi.com',
        'booking_com_flights': 'booking-com18.p.rapidapi.com',
        'booking_com_tipsters': 'tipsters.p.rapidapi.com',
        'flights_sky': 'flights-sky.p.rapidapi.com'
    }

def get_mock_flight_data(origin, destination, date, adults=1):
    """Generate mock flight data for demo mode"""
    return [
        {
            'id': f'flight1_{origin}_{destination}',
            'origin': origin,
            'destination': destination,
            'departureTime': '06:30',
            'arrivalTime': '09:15',
            'duration': '2h 45m',
            'price': 189 * adults,
            'airline': 'Ryanair',
            'stops': 0,
            'aircraft': 'Boeing 737',
            'date': date,
            'currency': 'GBP'
        },
        {
            'id': f'flight2_{origin}_{destination}',
            'origin': origin,
            'destination': destination,
            'departureTime': '14:20',
            'arrivalTime': '17:05',
            'duration': '2h 45m',
            'price': 245 * adults,
            'airline': 'Jet2',
            'stops': 0,
            'aircraft': 'Airbus A321',
            'date': date,
            'currency': 'GBP'
        }
    ]

def get_mock_deals_data():
    """Generate mock deals data for demo mode"""
    return [
        {
            'id': 1,
            'type': 'flight',
            'origin': 'EMA',
            'destination': 'ALC',
            'departureDate': '2024-09-15',
            'returnDate': '2024-09-22',
            'price': 189,
            'airline': 'Ryanair',
            'stops': 0,
            'duration': '2h 45m',
            'perPerson': 189,
            'totalPrice': 189,
            'flight': {
                'origin': 'EMA',
                'destination': 'ALC',
                'departure': '2024-09-15',
                'arrival': '2024-09-22',
                'carrier': 'Ryanair'
            },
            'hotel': {
                'stars': 4
            }
        },
        {
            'id': 2,
            'type': 'hotel',
            'name': 'Hotel Marina Delfin',
            'location': 'Alicante',
            'checkIn': '2024-09-15',
            'checkOut': '2024-09-22',
            'price': 420,
            'stars': 4,
            'board': 'RO',
            'perPerson': 210,
            'totalPrice': 420,
            'flight': {
                'origin': 'EMA',
                'destination': 'ALC',
                'departure': '2024-09-15',
                'arrival': '2024-09-22',
                'carrier': 'Hotel'
            },
            'hotel': {
                'stars': 4
            }
        },
        {
            'id': 3,
            'type': 'package',
            'origin': 'EMA',
            'destination': 'ALC',
            'departureDate': '2024-09-15',
            'returnDate': '2024-09-22',
            'flightPrice': 189,
            'hotelPrice': 420,
            'totalPrice': 609,
            'savings': 50,
            'perPerson': 304,
            'flight': {
                'origin': 'EMA',
                'destination': 'ALC',
                'departure': '2024-09-15',
                'arrival': '2024-09-22',
                'carrier': 'Ryanair'
            },
            'hotel': {
                'stars': 4
            }
        }
    ]

def get_rapidapi_headers(service):
    """Get RapidAPI headers for different services"""
    if RAPIDAPI_KEY == 'demo-key' or not RAPIDAPI_KEY:
        print("⚠️ Warning: Using demo mode - no real API calls will be made")
        return None
    return {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOSTS.get(service, 'google-flights2.p.rapidapi.com')
    }

def search_flights_realtime(origin, destination, date, adults=1, currency='GBP'):
    """Search for real-time flights using RapidAPI"""
    try:
        # Check if we have valid API credentials
        headers = get_rapidapi_headers('google_flights')
        if not headers:
            print("⚠️ Demo mode: Returning mock flight data")
            return get_mock_flight_data(origin, destination, date, adults)
        
        # Convert date to proper format for Google Flights API
        try:
            # Google Flights expects date in YYYY-MM-DD format
            if re.match(r'\d{4}-\d{2}-\d{2}', date):
                formatted_date = date
            else:
                # Parse and convert to YYYY-MM-DD format
                parsed_date = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = parsed_date.strftime('%Y-%m-%d')
        except:
            formatted_date = date
        
        # Google Flights search with proper parameters
        google_url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"
        google_params = {
            'departure_id': origin,
            'arrival_id': destination,
            'outbound_date': formatted_date,  # FIXED: Use outbound_date parameter
            'travel_class': 'ECONOMY',
            'adults': adults,
            'show_hidden': 1,
            'currency': currency,
            'language_code': 'en-GB',
            'country_code': 'GB',
            'search_type': 'best'
        }
        
        print(f"🔍 Google Flights API request: {google_params}")
        
        google_response = requests.get(
            google_url, 
            headers=headers,
            params=google_params
        )
        
        if google_response.status_code == 200:
            print(f"✅ Google Flights API successful!")
            return google_response.json()
        else:
            print(f"❌ Google Flights API error: {google_response.status_code}")
            print(f"Response: {google_response.text}")
            return None
            
    except Exception as e:
        print(f"Error searching real-time flights: {e}")
        return None

def search_flights_sky(origin, destination, date, adults=1, currency='GBP'):
    """Search for real-time flights using Flights Sky API"""
    try:
        # Convert date to ISO 8601 format if needed
        try:
            # If date is already in YYYY-MM-DD format, it's already ISO 8601
            if re.match(r'\d{4}-\d{2}-\d{2}', date):
                iso_date = date
            else:
                # Parse and convert to ISO format
                parsed_date = datetime.strptime(date, '%Y-%m-%d')
                iso_date = parsed_date.strftime('%Y-%m-%d')
        except:
            iso_date = date
        
        # Flights Sky search - using the correct endpoint from documentation
        sky_url = "https://flights-sky.p.rapidapi.com/search"
        sky_params = {
            'origin': origin,
            'destination': destination,
            'outbound_date': iso_date,  # Use outbound_date parameter
            'adults': adults,
            'currency': currency,
            'cabin_class': 'ECONOMY'
        }
        
        # Use the specific Flights Sky API key
        from config import RAPIDAPI_FLIGHTS_SKY_KEY
        sky_headers = {
            'X-RapidAPI-Key': RAPIDAPI_FLIGHTS_SKY_KEY,
            'X-RapidAPI-Host': 'flights-sky.p.rapidapi.com'
        }
        
        print(f"🔍 Flights Sky API request: {sky_params}")
        
        sky_response = requests.get(
            sky_url, 
            headers=sky_headers,
            params=sky_params
        )
        
        if sky_response.status_code == 200:
            return sky_response.json()
        else:
            print(f"Flights Sky API error: {sky_response.status_code}")
            print(f"Response: {sky_response.text}")
            return None
            
    except Exception as e:
        print(f"Error searching Flights Sky: {e}")
        return None

def search_booking_com_tipsters(origin, destination, date, adults=1, currency='GBP'):
    """Search for real-time flights using Booking.com Tipsters API"""
    try:
        # Convert date to proper format for Booking.com API
        try:
            # Booking.com expects date in YYYY-MM-DD format
            if re.match(r'\d{4}-\d{2}-\d{2}', date):
                formatted_date = date
            else:
                # Parse and convert to YYYY-MM-DD format
                parsed_date = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = parsed_date.strftime('%Y-%m-%d')
        except:
            formatted_date = date
        
        # Booking.com Tipsters search
        booking_url = "https://tipsters.p.rapidapi.com/flights/search"
        booking_params = {
            'origin': origin,
            'destination': destination,
            'departure_date': formatted_date,
            'adults': adults,
            'currency': currency,
            'cabin_class': 'ECONOMY'
        }
        
        # Use the specific Booking.com Tipsters API key
        from config import RAPIDAPI_BOOKING_TIPSTERS_KEY
        booking_headers = {
            'X-RapidAPI-Key': RAPIDAPI_BOOKING_TIPSTERS_KEY,
            'X-RapidAPI-Host': 'tipsters.p.rapidapi.com'
        }
        
        print(f"🔍 Booking.com Tipsters API request: {booking_params}")
        
        booking_response = requests.get(
            booking_url, 
            headers=booking_headers,
            params=booking_params
        )
        
        if booking_response.status_code == 200:
            print(f"✅ Booking.com Tipsters API successful!")
            return booking_response.json()
        else:
            print(f"❌ Booking.com Tipsters API error: {booking_response.status_code}")
            print(f"Response: {booking_response.text}")
            return None
            
    except Exception as e:
        print(f"Error searching Booking.com Tipsters: {e}")
        return None

def get_booking_url(flight_token):
    """Get booking URL for a specific flight using RapidAPI"""
    try:
        url = "https://google-flights2.p.rapidapi.com/api/v1/getBookingURL"
        data = {'token': flight_token}
        
        response = requests.post(
            url,
            headers=get_rapidapi_headers('google_flights'),
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Booking URL API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error getting booking URL: {e}")
        return None

def parse_flight_date(date_str):
    """Parse flight date from various formats and validate"""
    try:
        # Handle format like "25-08-2025 05:00 PM"
        if re.match(r'\d{2}-\d{2}-\d{4}', date_str):
            date_part = date_str.split(' ')[0]
            day, month, year = date_part.split('-')
            parsed_date = datetime(int(year), int(month), int(day))
        # Handle ISO format like "2025-08-25T17:00"
        elif re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', date_str):
            date_part = date_str.split('T')[0]
            year, month, day = date_part.split('-')
            parsed_date = datetime(int(year), int(month), int(day))
        else:
            return None, "Unknown date format"
        
        # Check if date is in the past
        if parsed_date < datetime.now():
            return None, "Date is in the past"
        
        # Check if date is too far in the future (more than 1 year)
        if parsed_date > datetime.now().replace(year=datetime.now().year + 1):
            return None, "Date is too far in the future"
        
        return parsed_date, None
    except Exception as e:
        return None, f"Date parsing error: {str(e)}"

def extract_airline_code(carrier):
    """Extract airline code from carrier string"""
    # Handle formats like "Ryanair FR 4818", "Jet2 LS 641"
    if carrier:
        parts = carrier.split()
        if len(parts) >= 2:
            return parts[1]  # Return the airline code (FR, LS, etc.)
    return None

def generate_working_booking_links(carrier, airline_code, origin="EMA", destination="ALC", date_str="25-08-2025", adults=2, nights=4):
    """Generate working booking links using RapidAPI and reliable fallbacks"""
    links = []
    
    # Parse date for URL
    try:
        if re.match(r'\d{2}-\d{2}-\d{4}', date_str):
            day, month, year = date_str.split(' ')[0].split('-')
            formatted_date = f"{year}-{month}-{day}"
        else:
            formatted_date = date_str
    except:
        formatted_date = date_str
    
    # Working airline booking URLs with proper search parameters
    if airline_code == 'FR':  # Ryanair
        # Calculate return date (departure + nights)
        try:
            departure_date = datetime.strptime(formatted_date, '%Y-%m-%d')
            return_date = departure_date + timedelta(days=nights)
            return_date_str = return_date.strftime('%Y-%m-%d')
        except:
            return_date_str = formatted_date
        
        # Create a proper Ryanair fare finder URL with your search parameters
        ryanair_url = (
            f"https://www.ryanair.com/gb/en/fare-finder?"
            f"originIata={origin}&"
            f"destinationIata={destination}&"
            f"isReturn=true&"
            f"isMacDestination=false&"
            f"promoCode=&"
            f"adults={adults}&"
            f"teens=0&"
            f"children=0&"
            f"infants=0&"
            f"dateOut={formatted_date}&"
            f"dateIn={return_date_str}&"
            f"nightsFrom={nights}&"
            f"nightsTo={nights}&"
            f"dayOfWeek=&"
            f"isExactDate=true&"
            f"outboundFromHour=00:00&"
            f"outboundToHour=23:59&"
            f"inboundFromHour=00:00&"
            f"inboundToHour=23:59&"
            f"priceValueTo=&"
            f"currency=GBP&"
            f"isFlexibleDay=false"
        )
        
        links.append({
            "type": "Ryanair Direct",
            "url": ryanair_url,
            "description": f"Book directly with Ryanair - {origin} to {destination} on {formatted_date}"
        })
    
    # Add reliable price comparison and search sites with pre-filled search parameters
    links.extend([
        {
            "type": "Google Flights",
            "url": f"https://www.google.com/travel/flights?hl=en&curr=GBP&f=0&t=1&q=Flights%20from%20{origin}%20to%20{destination}%20on%20{formatted_date}",
            "description": "Search on Google Flights"
        },
        {
            "type": "Skyscanner",
            "url": f"https://www.skyscanner.net/flights/{origin}/{destination}/{formatted_date}",
            "description": "Compare prices on Skyscanner"
        },
        {
            "type": "Kayak",
            "url": f"https://www.kayak.co.uk/flights/{origin}-{destination}/{formatted_date}",
            "description": "Search on Kayak"
        },
        {
            "type": "Expedia",
            "url": f"https://www.expedia.co.uk/Flights-Search?leg1=from:{origin},to:{destination},departure:{formatted_date}TANYT&passengers=adults:{adults},children:0,seniors:0,infantinlap:Y&mode=search&trip=oneway",
            "description": "Search on Expedia"
        }
    ])
    
    return links



@app.route('/api/deals', methods=['GET'])
def get_deals():
    """Get travel deals from the latest results"""
    try:
        # Load the latest results
        results_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'latest.json')
        
        if not os.path.exists(results_path):
            # Return mock data instead of error when no results file exists
            mock_deals = [
                {
                    'id': 1,
                    'type': 'flight',
                    'origin': 'EMA',
                    'destination': 'ALC',
                    'departureDate': '2024-09-15',
                    'returnDate': '2024-09-22',
                    'price': 189,
                    'airline': 'Ryanair',
                    'stops': 0,
                    'duration': '2h 45m',
                    'perPerson': 189,
                    'flight': {
                        'origin': 'EMA',
                        'destination': 'ALC',
                        'departure': '2024-09-15',
                        'arrival': '2024-09-22',
                        'carrier': 'Ryanair'
                    },
                    'hotel': {
                        'stars': 4
                    }
                },
                {
                    'id': 2,
                    'type': 'hotel',
                    'name': 'Hotel Marina Delfin',
                    'location': 'Alicante',
                    'checkIn': '2024-09-15',
                    'checkOut': '2024-09-22',
                    'price': 420,
                    'stars': 4,
                    'board': 'RO',
                    'perPerson': 210,
                    'flight': {
                        'origin': 'EMA',
                        'destination': 'ALC',
                        'departure': '2024-09-15',
                        'arrival': '2024-09-22',
                        'carrier': 'Hotel'
                    },
                    'hotel': {
                        'stars': 4
                    }
                },
                {
                    'id': 3,
                    'type': 'package',
                    'origin': 'EMA',
                    'destination': 'ALC',
                    'departureDate': '2024-09-15',
                    'returnDate': '2024-09-22',
                    'flightPrice': 189,
                    'hotelPrice': 420,
                    'totalPrice': 609,
                    'savings': 50,
                    'perPerson': 304,
                    'flight': {
                        'origin': 'EMA',
                        'destination': 'ALC',
                        'departure': '2024-09-15',
                        'arrival': '2024-09-22',
                        'carrier': 'Ryanair'
                    },
                    'hotel': {
                        'stars': 4
                    }
                }
            ]
            
            return jsonify({
                'deals': mock_deals,
                'total': len(mock_deals),
                'timestamp': datetime.now().isoformat(),
                'source': 'mock_data'
            })
        
        with open(results_path, 'r') as f:
            data = json.load(f)
        
        # Filter deals based on query parameters if provided
        deals = data.get('deals', [])
        
        # Apply filters if query parameters are provided
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        max_price = request.args.get('max_price')
        min_stars = request.args.get('min_stars')
        
        if origin:
            deals = [deal for deal in deals if deal.get('flight', {}).get('origin') == origin]
        
        if destination:
            deals = [deal for deal in deals if deal.get('flight', {}).get('destination') == destination]
        
        if max_price:
            try:
                max_price = float(max_price)
                deals = [deal for deal in deals if deal.get('perPerson', 0) <= max_price]
            except ValueError:
                pass
        
        if min_stars:
            try:
                min_stars = int(min_stars)
                deals = [deal for deal in deals if deal.get('hotel', {}).get('stars', 0) >= min_stars]
            except ValueError:
                pass
        
        return jsonify({
            'deals': deals,
            'total': len(deals),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/search', methods=['POST'])
def search_deals():
    """Search for deals based on search parameters"""
    try:
        data = request.get_json()
        
        # Load the latest results
        results_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'latest.json')
        
        if not os.path.exists(results_path):
            # Return mock data instead of error when no results file exists
            mock_deals = [
                {
                    'id': 1,
                    'type': 'flight',
                    'origin': 'EMA',
                    'destination': 'ALC',
                    'departureDate': '2024-09-15',
                    'returnDate': '2024-09-22',
                    'price': 189,
                    'airline': 'Ryanair',
                    'stops': 0,
                    'duration': '2h 45m',
                    'perPerson': 189,
                    'flight': {
                        'origin': 'EMA',
                        'destination': 'ALC',
                        'departure': '2024-09-15',
                        'arrival': '2024-09-22',
                        'carrier': 'Ryanair'
                    },
                    'hotel': {
                        'stars': 4
                    }
                },
                {
                    'id': 2,
                    'type': 'hotel',
                    'name': 'Hotel Marina Delfin',
                    'location': 'Alicante',
                    'checkIn': '2024-09-15',
                    'checkOut': '2024-09-22',
                    'price': 420,
                    'stars': 4,
                    'board': 'RO',
                    'perPerson': 210,
                    'flight': {
                        'origin': 'EMA',
                        'destination': 'ALC',
                        'departure': '2024-09-15',
                        'arrival': '2024-09-22',
                        'carrier': 'Hotel'
                    },
                    'hotel': {
                        'stars': 4
                    }
                },
                {
                    'id': 3,
                    'type': 'package',
                    'origin': 'EMA',
                    'destination': 'ALC',
                    'departureDate': '2024-09-15',
                    'returnDate': '2024-09-22',
                    'flightPrice': 189,
                    'hotelPrice': 420,
                    'totalPrice': 609,
                    'savings': 50,
                    'perPerson': 304,
                    'flight': {
                        'origin': 'EMA',
                        'destination': 'ALC',
                        'departure': '2024-09-15',
                        'arrival': '2024-09-22',
                        'carrier': 'Ryanair'
                    },
                    'hotel': {
                        'stars': 4
                    }
                }
            ]
            
            # Apply search filters to mock data
            if data.get('budgetPerPerson'):
                try:
                    budget = float(data['budgetPerPerson'])
                    mock_deals = [deal for deal in mock_deals if deal.get('perPerson', 0) <= budget]
                except ValueError:
                    pass
            
            if data.get('minStars'):
                try:
                    min_stars = int(data['minStars'])
                    mock_deals = [deal for deal in mock_deals if deal.get('hotel', {}).get('stars', 0) >= min_stars]
                except ValueError:
                    pass
            
            return jsonify({
                'deals': mock_deals,
                'total': len(mock_deals),
                'timestamp': datetime.now().isoformat(),
                'source': 'mock_data'
            })
        
        # If we have real data, load it
        with open(results_path, 'r') as f:
            results_data = json.load(f)
        
        deals = results_data.get('deals', [])
        
        # Apply search filters based on available data
        if data.get('budgetPerPerson'):
            try:
                budget = float(data['budgetPerPerson'])
                deals = [deal for deal in deals if deal.get('perPerson', 0) <= budget]
            except ValueError:
                pass
        
        if data.get('minStars'):
            try:
                min_stars = int(data['minStars'])
                deals = [deal for deal in deals if deal.get('hotel', {}).get('stars', 0) >= min_stars]
            except ValueError:
                pass
        
        # NEW: Filter by departure date if provided
        if data.get('departureDate'):
            try:
                # Parse the search date (format: "2025-08-28")
                search_date = datetime.strptime(data['departureDate'], '%Y-%m-%d')
                
                # Filter deals by departure date
                filtered_deals = []
                for deal in deals:
                    flight = deal.get('flight', {})
                    departure_str = flight.get('departure', '')
                    
                    if departure_str:
                        # Parse the deal's departure date
                        deal_date, _ = parse_flight_date(departure_str)
                        if deal_date and deal_date.date() == search_date.date():
                            filtered_deals.append(deal)
                
                deals = filtered_deals
                print(f"Date filtering: search for {data['departureDate']}, found {len(filtered_deals)} deals")
            except Exception as e:
                print(f"Date filtering error: {e}")
                # If date filtering fails, continue with all deals
        
        # Enhance the deals with booking links and date validation
        enhanced_deals = []
        for deal in deals:
            flight = deal.get('flight', {})
            
            # Parse and validate flight dates
            departure_date, departure_error = parse_flight_date(flight.get('departure', ''))
            arrival_date, arrival_error = parse_flight_date(flight.get('arrival', ''))
            
            # Extract airline code
            airline_code = extract_airline_code(flight.get('carrier', ''))
            
            # Generate direct booking links
            booking_links = generate_working_booking_links(
                flight.get('carrier', ''),
                airline_code,
                origin="EMA",  # Default from your data
                destination="ALC",  # Default from your data
                date_str=flight.get('departure', ''),
                adults=data.get('adults', 2),  # Get from search params or default to 2
                nights=data.get('nights', 4)   # Get from search params or default to 4
            )
            
            # Create enhanced deal
            enhanced_deal = {
                **deal,
                'flight': {
                    **flight,
                    'departureDate': departure_date.isoformat() if departure_date else None,
                    'departureError': departure_error,
                    'arrivalDate': arrival_date.isoformat() if arrival_date else None,
                    'arrivalError': arrival_error,
                    'airlineCode': airline_code,
                    'bookingLinks': booking_links,
                    'isDateValid': departure_date is not None and arrival_date is not None
                }
            }
            
            enhanced_deals.append(enhanced_deal)
        
        return jsonify({
            'deals': enhanced_deals,
            'total': len(enhanced_deals),
            'searchParams': data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/enhanced', methods=['GET'])
def get_enhanced_deals():
    """Get travel deals with enhanced booking information and date validation"""
    try:
        # Load the latest results
        results_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'latest.json')
        
        if not os.path.exists(results_path):
            return jsonify({'error': 'No results found'}), 404
        
        with open(results_path, 'r') as f:
            data = json.load(f)
        
        enhanced_deals = []
        for deal in data.get('deals', []):
            flight = deal.get('flight', {})
            
            # Parse and validate flight dates
            departure_date, departure_error = parse_flight_date(flight.get('departure', ''))
            arrival_date, arrival_error = parse_flight_date(flight.get('arrival', ''))
            
            # Extract airline code
            airline_code = extract_airline_code(flight.get('carrier', ''))
            
            # Generate direct booking links
            booking_links = generate_working_booking_links(
                flight.get('carrier', ''),
                airline_code,
                origin="EMA",  # Default from your data
                destination="ALC",  # Default from your data
                date_str=flight.get('departure', ''),
                adults=2,  # Default for enhanced deals
                nights=4   # Default for enhanced deals
            )
            
            # Create enhanced deal
            enhanced_deal = {
                **deal,
                'flight': {
                    **flight,
                    'departureDate': departure_date.isoformat() if departure_date else None,
                    'departureError': departure_error,
                    'arrivalDate': arrival_date.isoformat() if arrival_date else None,
                    'arrivalError': arrival_error,
                    'airlineCode': airline_code,
                    'bookingLinks': booking_links,
                    'isDateValid': departure_date is not None and arrival_date is not None
                }
            }
            
            enhanced_deals.append(enhanced_deal)
        
        return jsonify({
            'deals': enhanced_deals,
            'total': len(enhanced_deals),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flights/search', methods=['POST'])
def search_realtime_flights():
    """Search for real-time flights using RapidAPI"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        origin = data.get('origin', 'EMA')
        destination = data.get('destination', 'ALC')
        date = data.get('date')
        adults = data.get('adults', 1)
        currency = data.get('currency', 'GBP')
        
        # Try Google Flights first
        print(f"🔍 Searching Google Flights: {origin} → {destination} on {date}")
        flight_results = search_flights_realtime(origin, destination, date, adults, currency)
        
        # If Google Flights fails, try Flights Sky as fallback
        if not flight_results:
            print(f"🔄 Google Flights failed, trying Flights Sky API...")
            flight_results = search_flights_sky(origin, destination, date, adults, currency)
            
            if flight_results:
                print(f"✅ Flights Sky API successful!")
            else:
                print(f"🔄 Flights Sky failed, trying Booking.com Tipsters API...")
                flight_results = search_booking_com_tipsters(origin, destination, date, adults, currency)
                
                if flight_results:
                    print(f"✅ Booking.com Tipsters API successful!")
                else:
                    print(f"❌ All three APIs failed")
        
        if flight_results:
            return jsonify({
                'success': True,
                'data': flight_results,
                'searchParams': data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No flights found or API error',
                'searchParams': data,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flights/booking-url', methods=['POST'])
def get_flight_booking_url():
    """Get booking URL for a specific flight"""
    try:
        data = request.get_json()
        flight_token = data.get('token')
        
        if not flight_token:
            return jsonify({'error': 'Flight token required'}), 400
        
        # Get booking URL
        booking_data = get_booking_url(flight_token)
        
        if booking_data:
            return jsonify({
                'success': True,
                'data': booking_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not get booking URL',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
