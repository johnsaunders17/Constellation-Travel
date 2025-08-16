import React, { useState, useEffect } from 'react';
import { airports, searchAirports, Airport } from '../config/airports';
import { fetchLatestResults, Deal } from '../lib/results';
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

  // Filter airports for dropdowns
  const filteredOriginAirports = searchAirports(originSearch);
  const filteredDestinationAirports = searchAirports(destinationSearch);

  const handleSearch = async () => {
    setIsSearching(true);
    setShowResults(true);
    
    try {
      // In a real app, you'd call your backend API here
      // For now, we'll simulate the search and show existing results
      const results = await fetchLatestResults(import.meta.env.BASE_URL);
      setDeals(results?.deals ?? []);
    } catch (error) {
      console.error('Search failed:', error);
      setDeals([]);
    } finally {
      setIsSearching(false);
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

                {/* Search Button */}
                <div className="form-row">
                  <button
                    type="button"
                    onClick={handleSearch}
                    disabled={isSearching}
                    className="search-button"
                  >
                    {isSearching ? 'Searching...' : 'Search Deals'}
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
                {getAirportDisplay(searchParams.origin)} → {getAirportDisplay(searchParams.destination)}
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
                  <div key={idx} className="deal-card">
                    <div className="deal-header">
                      <div className="deal-price">
                        <span className="price-main">{formatPrice(deal.perPerson)}</span>
                        <span className="price-sub">per person</span>
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
                          <span className="value">{new Date(deal.flight.departure).toLocaleDateString()}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Duration:</span>
                          <span className="value">{deal.flight.duration}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Stops:</span>
                          <span className="value">{deal.flight.stops}</span>
                        </div>
                        {deal.flight.link && (
                          <a href={deal.flight.link} target="_blank" rel="noopener noreferrer" className="book-link">
                            Book Flight
                          </a>
                        )}
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
      </main>
    </div>
  );
}
