export interface FlightDeal {
  provider: string
  price: number
  carrier: string
  departure: string
  arrival: string
  link: string
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
  const url = `${base}../results/latest.json`.replace(/\/+/, '/');
  const res = await fetch(url, { cache: 'no-store' })
  if (!res.ok) return null
  const json = await res.json()
  return json as Results
}
