export interface FlightDeal {
  provider: string
  price: number
  carrier: string
  departure: string
  arrival: string
  link: string
  // Enhanced fields
  departureDate?: string
  departureError?: string
  arrivalDate?: string
  arrivalError?: string
  airlineCode?: string
  bookingLinks?: BookingLink[]
  isDateValid?: boolean
}

export interface HotelDeal {
  provider: string
  name: string
  stars: number
  rating: number
  board: string
  price: number
  link: string
}

export interface BookingLink {
  type: string
  url: string
  description: string
}

export interface Deal {
  timestamp: string
  perPerson: number
  total: number
  flight: FlightDeal
  hotel: HotelDeal
}

export interface Results {
  deals: Deal[]
  count: number
  queriedAt: string
}

export async function fetchLatestResults(base = ''): Promise<Results | null> {
  try {
    // Use the enhanced Flask API endpoint
    const url = 'http://localhost:5001/api/deals/enhanced';
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) return null;
    const json = await res.json();
    
    // Transform the API response to match our interface
    return {
      deals: json.deals || [],
      count: json.total || 0,
      queriedAt: json.timestamp || new Date().toISOString()
    };
  } catch (error) {
    console.error('Error fetching results:', error);
    return null;
  }
}
