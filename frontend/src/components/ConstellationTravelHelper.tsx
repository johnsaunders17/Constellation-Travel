import React, { useState, useEffect } from 'react';
import { airports, searchAirports, Airport } from '../config/airports';
import { fetchLatestResults, Deal } from '../lib/results';
import { buildApiUrl, API_ENDPOINTS, MOCK_DATA } from '../config/api';
import './ConstellationTravelHelper.css';

interface SearchParams {
  origin: string;
  destination: string;
  departureDate: string;
  nights: number;
  adults: number;
  children: number;
  cabin: string;
  tripType: 'roundtrip' | 'oneway';
  includeHotels: boolean;
  minStars: number;
  board: string;
  budgetPerPerson: number;
}

export default function ConstellationTravelHelper() {
  const [searchParams, setSearchParams] = useState<SearchParams>({
    origin: 'EMA',
    destination: 'ALC',
    departureDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days from now
    nights: 7,
    adults: 2,
    children: 0,
    cabin: 'ECONOMY',
    tripType: 'roundtrip',
    includeHotels: true,
    minStars: 3,
    board: 'RO',
    budgetPerPerson: 700
  });

  const [deals, setDeals] = useState<Deal[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [originSearch, setOriginSearch] = useState('');
  const [destinationSearch, setDestinationSearch] = useState('');
  const [showOriginDropdown, setShowOriginDropdown] = useState(false);
  const [showDestinationDropdown, setShowDestinationDropdown] = useState(false);
  
  // New state for real-time flight search
  const [realtimeFlights, setRealtimeFlights] = useState<any[] | null>(null);
  const [isSearchingRealtime, setIsSearchingRealtime] = useState(false);
  const [showRealtimeResults, setShowRealtimeResults] = useState(false);

  // Filter airports for dropdowns
  const filteredOriginAirports = searchAirports(originSearch);
  const filteredDestinationAirports = searchAirports(destinationSearch);

  // Load initial deals when component mounts
  useEffect(() => {
    const loadInitialDeals = async () => {
      try {
        const response = await fetch(buildApiUrl(API_ENDPOINTS.deals));
        if (response.ok) {
          const data = await response.json();
          setDeals(data.deals || []);
        } else {
          // Fallback to mock data if API fails
          console.log('API failed, using mock data');
          setDeals(MOCK_DATA.deals);
        }
      } catch (error) {
        console.error('Failed to load initial deals, using mock data:', error);
        // Fallback to mock data
        setDeals(MOCK_DATA.deals);
      }
    };
    
    loadInitialDeals();
  }, []);

  const handleSearch = async () => {
    console.log('🔍 Search button clicked!');
    console.log('Search params:', searchParams);
    
    setIsSearching(true);
    setShowResults(true);
    
    try {
      const searchBody = {
        budgetPerPerson: searchParams.budgetPerPerson,
        minStars: searchParams.minStars,
        departureDate: searchParams.departureDate, // NEW: Include departure date for filtering
        // Note: origin/destination filtering not available in current data
      };
      
      console.log('Sending search request with body:', searchBody);
      
      // Call the enhanced Flask API with search parameters
      const response = await fetch(buildApiUrl(API_ENDPOINTS.search), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchBody),
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error('Search failed');
      }
      
      const data = await response.json();
      console.log('Search response:', data);
      console.log('Found deals:', data.deals?.length || 0);
      
      setDeals(data.deals || []);
    } catch (error) {
      console.error('Search failed, using mock data:', error);
      // Fallback to mock data
      setDeals(MOCK_DATA.deals);
    } finally {
      setIsSearching(false);
    }
  };

  const handleRealtimeSearch = async () => {
    console.log('🚀 Real-time search button clicked!');
    console.log('Real-time search params:', {
      origin: searchParams.origin,
      destination: searchParams.destination,
      date: searchParams.departureDate,
      adults: searchParams.adults
    });
    
    setIsSearchingRealtime(true);
    setShowRealtimeResults(true);
    
    try {
      const realtimeBody = {
        origin: searchParams.origin,
        destination: searchParams.destination,
        date: searchParams.departureDate,
        adults: searchParams.adults,
        currency: 'GBP'
      };
      
      console.log('Sending real-time search request with body:', realtimeBody);
      
      // Call the new real-time flight search API
      const response = await fetch(buildApiUrl(API_ENDPOINTS.flightsSearch), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(realtimeBody),
      });
      
      console.log('Real-time response status:', response.status);
      
      if (!response.ok) {
        throw new Error('Real-time search failed');
      }
      
      const data = await response.json();
      console.log('Real-time search response:', data);
      
      if (data.success && data.data) {
        setRealtimeFlights(data.data);
        console.log('Real-time flights found:', data.data.length);
      } else {
        setRealtimeFlights([]);
        console.log('No real-time flights found');
      }
    } catch (error) {
      console.error('Real-time search failed, using mock data:', error);
      // Fallback to mock data
      setRealtimeFlights(MOCK_DATA.flights);
    } finally {
      setIsSearchingRealtime(false);
    }
  };

  const formatPrice = (price: number) => `£${price.toFixed(0)}`;

  const getAirportDisplay = (code: string) => {
    const airport = airports.find(a => a.code === code);
    return airport ? `${airport.city} (${airport.code})` : code;
  };

  return (
    <div className="constellation-travel">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1 className="logo">Constellation Travel</h1>
          <p className="tagline">Discover the stars, explore the world</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {!showResults ? (
          /* Search Form */
          <div className="search-container">
            <div className="search-card">
              <h2>Find Your Perfect Trip</h2>
              
              <div className="search-form">
                {/* Trip Type Selection */}
                <div className="form-row">
                  <div className="form-group">
                    <label>Trip Type</label>
                    <div className="trip-type-buttons">
                      <button
                        type="button"
                        className={`trip-type-btn ${searchParams.tripType === 'roundtrip' ? 'active' : ''}`}
                        onClick={() => setSearchParams({...searchParams, tripType: 'roundtrip'})}
                      >
                        Round Trip
                      </button>
                      <button
                        type="button"
                        className={`trip-type-btn ${searchParams.tripType === 'oneway' ? 'active' : ''}`}
                        onClick={() => setSearchParams({...searchParams, tripType: 'oneway'})}
                      >
                        One Way
                      </button>
                    </div>
                  </div>
                </div>

                {/* Origin and Destination */}
                <div className="form-row">
                  <div className="form-group">
                    <label>Flying From</label>
                    <div className="airport-input-container">
                      <input
                        type="text"
                        placeholder="Search airports..."
                        value={originSearch}
                        onChange={(e) => setOriginSearch(e.target.value)}
                        onFocus={() => setShowOriginDropdown(true)}
                        className="airport-input"
                      />
                      {showOriginDropdown && (
                        <div className="airport-dropdown">
                          {filteredOriginAirports.map((airport) => (
                            <div
                              key={airport.code}
                              className="airport-option"
                              onClick={() => {
                                setSearchParams({...searchParams, origin: airport.code});
                                setOriginSearch(`${airport.city} (${airport.code})`);
                                setShowOriginDropdown(false);
                              }}
                            >
                              <div className="airport-name">{airport.city} ({airport.code})</div>
                              <div className="airport-details">{airport.name}, {airport.country}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Flying To</label>
                    <div className="airport-input-container">
                      <input
                        type="text"
                        placeholder="Search airports..."
                        value={destinationSearch}
                        onChange={(e) => setDestinationSearch(e.target.value)}
                        onFocus={() => setShowDestinationDropdown(true)}
                        className="airport-input"
                      />
                      {showDestinationDropdown && (
                        <div className="airport-dropdown">
                          {filteredDestinationAirports.map((airport) => (
                            <div
                              key={airport.code}
                              className="airport-option"
                              onClick={() => {
                                setSearchParams({...searchParams, destination: airport.code});
                                setDestinationSearch(`${airport.city} (${airport.code})`);
                                setShowDestinationDropdown(false);
                              }}
                            >
                              <div className="airport-name">{airport.city} ({airport.code})</div>
                              <div className="airport-details">{airport.name}, {airport.country}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Dates and Duration */}
                <div className="form-row">
                  <div className="form-group">
                    <label>Departure Date</label>
                    <input
                      type="date"
                      value={searchParams.departureDate}
                      onChange={(e) => setSearchParams({...searchParams, departureDate: e.target.value})}
                      min={new Date().toISOString().split('T')[0]}
                      className="form-input"
                    />
                  </div>

                  {searchParams.tripType === 'roundtrip' && (
                    <div className="form-group">
                      <label>Duration</label>
                      <select
                        value={searchParams.nights}
                        onChange={(e) => setSearchParams({...searchParams, nights: parseInt(e.target.value)})}
                        className="form-input"
                      >
                        <option value={1}>1 night</option>
                        <option value={2}>2 nights</option>
                        <option value={3}>3 nights</option>
                        <option value={4}>4 nights</option>
                        <option value={5}>5 nights</option>
                        <option value={6}>6 nights</option>
                        <option value={7}>7 nights</option>
                        <option value={10}>10 nights</option>
                        <option value={14}>14 nights</option>
                        <option value={21}>21 nights</option>
                      </select>
                    </div>
                  )}
                </div>

                {/* Passengers */}
                <div className="form-row">
                  <div className="form-group">
                    <label>Adults (16+)</label>
                    <select
                      value={searchParams.adults}
                      onChange={(e) => setSearchParams({...searchParams, adults: parseInt(e.target.value)})}
                      className="form-input"
                    >
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(num => (
                        <option key={num} value={num}>{num}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Children (0-15)</label>
                    <select
                      value={searchParams.children}
                      onChange={(e) => setSearchParams({...searchParams, children: parseInt(e.target.value)})}
                      className="form-input"
                    >
                      {[0, 1, 2, 3, 4, 5, 6].map(num => (
                        <option key={num} value={num}>{num}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Cabin Class</label>
                    <select
                      value={searchParams.cabin}
                      onChange={(e) => setSearchParams({...searchParams, cabin: e.target.value})}
                      className="form-input"
                    >
                      <option value="ECONOMY">Economy</option>
                      <option value="PREMIUM_ECONOMY">Premium Economy</option>
                      <option value="BUSINESS">Business</option>
                      <option value="FIRST">First</option>
                    </select>
                  </div>
                </div>

                {/* Hotel Options */}
                <div className="form-row">
                  <div className="form-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={searchParams.includeHotels}
                        onChange={(e) => setSearchParams({...searchParams, includeHotels: e.target.checked})}
                      />
                      Include Hotels
                    </label>
                  </div>
                </div>

                {searchParams.includeHotels && (
                  <div className="hotel-options">
                    <div className="form-row">
                      <div className="form-group">
                        <label>Minimum Hotel Stars</label>
                        <select
                          value={searchParams.minStars}
                          onChange={(e) => setSearchParams({...searchParams, minStars: parseInt(e.target.value)})}
                          className="form-input"
                        >
                          <option value={1}>1★</option>
                          <option value={2}>2★</option>
                          <option value={3}>3★</option>
                          <option value={4}>4★</option>
                          <option value={5}>5★</option>
                        </select>
                      </div>

                      <div className="form-group">
                        <label>Board Type</label>
                        <select
                          value={searchParams.board}
                          onChange={(e) => setSearchParams({...searchParams, board: e.target.value})}
                          className="form-input"
                        >
                          <option value="RO">Room Only</option>
                          <option value="BB">Bed & Breakfast</option>
                          <option value="HB">Half Board</option>
                          <option value="FB">Full Board</option>
                          <option value="AI">All Inclusive</option>
                        </select>
                      </div>

                      <div className="form-group">
                        <label>Budget per Person</label>
                        <input
                          type="number"
                          value={searchParams.budgetPerPerson}
                          onChange={(e) => setSearchParams({...searchParams, budgetPerPerson: parseInt(e.target.value)})}
                          placeholder="700"
                          className="form-input"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Search Buttons */}
                <div className="form-row">
                  <button
                    type="button"
                    onClick={handleSearch}
                    disabled={isSearching}
                    className="search-button"
                  >
                    {isSearching ? 'Searching...' : 'Search Deals'}
                  </button>
                  
                  <button
                    type="button"
                    onClick={handleRealtimeSearch}
                    disabled={isSearchingRealtime}
                    className="search-button realtime"
                  >
                    {isSearchingRealtime ? 'Searching...' : '🔍 Real-Time Search'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Results Page */
          <div className="results-container">
            <div className="results-header">
              <button
                onClick={() => setShowResults(false)}
                className="back-button"
              >
                ← New Search
              </button>
              <h2>Travel Deals Found</h2>
              <div className="search-summary">
                <div>Showing deals for your budget and preferences</div>
                <div className="search-note">
                  Note: Origin/destination filtering not available in current data
                </div>
                {searchParams.tripType === 'roundtrip' && ` • ${searchParams.nights} nights`}
                {searchParams.includeHotels && ` • Hotels included`}
              </div>
            </div>

            {isSearching ? (
              <div className="loading">
                <div className="spinner"></div>
                <p>Searching for the best deals...</p>
              </div>
            ) : deals && deals.length > 0 ? (
              <div className="deals-grid">
                {deals.slice(0, 20).map((deal, idx) => (
                  <div key={idx} className={`deal-card ${!deal.flight.isDateValid ? 'invalid-date' : ''}`}>
                    <div className="deal-header">
                      <div className="deal-price">
                        <span className="price-main">{formatPrice(deal.perPerson)}</span>
                        <span className="price-sub">per person</span>
                        {!deal.flight.isDateValid && (
                          <span className="invalid-date-badge">⚠️ Invalid Date</span>
                        )}
                      </div>
                      <div className="deal-total">
                        Total: {formatPrice(deal.total)}
                      </div>
                    </div>

                    <div className="deal-details">
                      <div className="flight-details">
                        <h4>✈️ Flight</h4>
                        <div className="detail-row">
                          <span className="label">Airline:</span>
                          <span className="value">{deal.flight.carrier}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Departure:</span>
                          <span className="value">
                            {deal.flight.departureDate ? 
                              new Date(deal.flight.departureDate).toLocaleDateString('en-GB', {
                                weekday: 'short',
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric'
                              }) : 
                              deal.flight.departure
                            }
                            {deal.flight.departureError && (
                              <span className="date-error">⚠️ {deal.flight.departureError}</span>
                            )}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Duration:</span>
                          <span className="value">{deal.flight.duration}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Stops:</span>
                          <span className="value">{deal.flight.stops}</span>
                        </div>
                        {/* Booking Links */}
                        <div className="booking-links">
                          <h5>Book This Flight:</h5>
                          <div className="booking-info">
                            <p className="booking-note">
                              ✈️ <strong>Direct Airline</strong> - Book directly with Ryanair (when available)
                            </p>
                            <p className="booking-note">
                              🔍 <strong>Search & Compare</strong> - Find the best prices across all airlines
                            </p>
                          </div>
                          {deal.flight.bookingLinks && deal.flight.bookingLinks.length > 0 ? (
                            <div className="booking-options">
                              {deal.flight.bookingLinks.map((link, linkIdx) => (
                                <a 
                                  key={linkIdx}
                                  href={link.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer" 
                                  className={`book-link ${link.type === 'Direct Airline' ? 'primary' : 'secondary'}`}
                                  title={`Click to ${link.description.toLowerCase()}`}
                                >
                                  {link.type === 'Direct Airline' ? '✈️ ' : '🔍 '}
                                  {link.description}
                                </a>
                              ))}
                            </div>
                          ) : deal.flight.link ? (
                            <a href={deal.flight.link} target="_blank" rel="noopener noreferrer" className="book-link">
                              Book Flight
                            </a>
                          ) : (
                            <span className="no-booking">No booking link available</span>
                          )}
                        </div>
                      </div>

                      {deal.hotel && (
                        <div className="hotel-details">
                          <h4>🏨 Hotel</h4>
                          <div className="detail-row">
                            <span className="label">Name:</span>
                            <span className="value">{deal.hotel.name}</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Rating:</span>
                            <span className="value">{'★'.repeat(deal.hotel.stars)}</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Board:</span>
                            <span className="value">{deal.hotel.board}</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Price:</span>
                            <span className="value">{formatPrice(deal.hotel.price)}</span>
                          </div>
                          {deal.hotel.link && (
                            <a href={deal.hotel.link} target="_blank" rel="noopener noreferrer" className="book-link">
                              Book Hotel
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-results">
                <p>No deals found for your search criteria.</p>
                <p>Try adjusting your dates, destination, or budget.</p>
              </div>
            )}
          </div>
        )}

        {/* Real-Time Flight Results */}
        {showRealtimeResults && (
          <div className="results-container">
            <div className="results-header">
              <button
                onClick={() => setShowRealtimeResults(false)}
                className="back-button"
              >
                ← New Search
              </button>
              <h2>Real-Time Flight Results</h2>
              <div className="search-summary">
                <div>Live search results from Google Flights API</div>
                <div className="search-note">
                  Real-time pricing and availability
                </div>
                {searchParams.origin} → {searchParams.destination} • {searchParams.departureDate}
              </div>
            </div>

            {isSearchingRealtime ? (
              <div className="loading">
                <div className="spinner"></div>
                <p>Searching for real-time flights...</p>
              </div>
            ) : realtimeFlights && realtimeFlights.length > 0 ? (
              <div className="deals-grid">
                {realtimeFlights.slice(0, 20).map((flight, idx) => (
                  <div key={idx} className="deal-card realtime">
                    <div className="deal-header">
                      <div className="deal-price">
                        <span className="price-main">£{flight.price || 'N/A'}</span>
                        <span className="price-sub">per person</span>
                        <span className="realtime-badge">🔄 LIVE</span>
                      </div>
                      <div className="deal-total">
                        Airline: {flight.airline || 'Unknown'}
                      </div>
                    </div>

                    <div className="deal-details">
                      <div className="flight-details">
                        <h4>✈️ Flight Details</h4>
                        <div className="detail-row">
                          <span className="label">From:</span>
                          <span className="value">{searchParams.origin}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">To:</span>
                          <span className="value">{searchParams.destination}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Date:</span>
                          <span className="value">{searchParams.departureDate}</span>
                        </div>
                        {flight.duration && (
                          <div className="detail-row">
                            <span className="label">Duration:</span>
                            <span className="value">{flight.duration}</span>
                          </div>
                        )}
                        {flight.stops !== undefined && (
                          <div className="detail-row">
                            <span className="label">Stops:</span>
                            <span className="value">{flight.stops}</span>
                          </div>
                        )}
                      </div>

                      {/* Real-time booking links */}
                      <div className="booking-links">
                        <h5>Book This Flight:</h5>
                        <div className="booking-options">
                          <a 
                            href={`https://www.google.com/travel/flights?hl=en&curr=GBP&f=0&t=1&q=Flights%20from%20${searchParams.origin}%20to%20${searchParams.destination}%20on%20${searchParams.departureDate}`}
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="book-link primary"
                          >
                            🔍 Search on Google Flights
                          </a>
                          <a 
                            href={`https://www.skyscanner.net/flights/${searchParams.origin}/${searchParams.destination}/${searchParams.departureDate}`}
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="book-link secondary"
                          >
                            Compare on Skyscanner
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-results">
                <p>No real-time flights found for your search criteria.</p>
                <p>Try adjusting your dates, destination, or check if the RapidAPI key is configured.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
