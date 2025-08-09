import React, { useEffect, useState } from 'react'
import { fetchLatestResults, Deal } from '../lib/results'

export default function ConstellationTravelHelper() {
  const [deals, setDeals] = useState<Deal[] | null>(null)

  useEffect(() => {
    fetchLatestResults(import.meta.env.BASE_URL).then((data) => {
      setDeals(data?.deals ?? [])
    })
  }, [])

  return (
    <div>
      <h1>Constellation Travel Helper</h1>
      {deals === null ? (
        <p>Loading...</p>
      ) : deals.length > 0 ? (
        <ul>
          {deals.map((deal, idx) => (
            <li key={idx}>
              <div>
                <h2>
                  £{deal.perPerson} per person (£{deal.total} total)
                </h2>
                <div>
                  <strong>Flight:</strong> {deal.flight.carrier} from
                  {' '}
                  {new Date(deal.flight.departure).toLocaleString()} to{' '}
                  {new Date(deal.flight.arrival).toLocaleString()}
                </div>
                <div>
                  <strong>Hotel:</strong> {deal.hotel.name} ({deal.hotel.stars}★{' '}
                  {deal.hotel.board})
                </div>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p>No deals available.</p>
      )}
    </div>
  )
}
