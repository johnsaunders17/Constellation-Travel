export interface Airport {
  code: string;
  name: string;
  city: string;
  country: string;
}

export const airports: Airport[] = [
  // UK Airports
  { code: "EMA", name: "East Midlands", city: "East Midlands", country: "United Kingdom" },
  { code: "BHX", name: "Birmingham", city: "Birmingham", country: "United Kingdom" },
  { code: "MAN", name: "Manchester", city: "Manchester", country: "United Kingdom" },
  { code: "LHR", name: "Heathrow", city: "London", country: "United Kingdom" },
  { code: "LGW", name: "Gatwick", city: "London", country: "United Kingdom" },
  { code: "STN", name: "Stansted", city: "London", country: "United Kingdom" },
  { code: "LTN", name: "Luton", city: "London", country: "United Kingdom" },
  { code: "LPL", name: "Liverpool", city: "Liverpool", country: "United Kingdom" },
  { code: "BRS", name: "Bristol", city: "Bristol", country: "United Kingdom" },
  { code: "EDI", name: "Edinburgh", city: "Edinburgh", country: "United Kingdom" },
  { code: "GLA", name: "Glasgow", city: "Glasgow", country: "United Kingdom" },
  { code: "NCL", name: "Newcastle", city: "Newcastle", country: "United Kingdom" },
  { code: "CWL", name: "Cardiff", city: "Cardiff", country: "United Kingdom" },
  
  // Spain
  { code: "ALC", name: "Alicante", city: "Alicante", country: "Spain" },
  { code: "BCN", name: "Barcelona", city: "Barcelona", country: "Spain" },
  { code: "MAD", name: "Madrid", city: "Madrid", country: "Spain" },
  { code: "PMI", name: "Palma de Mallorca", city: "Palma", country: "Spain" },
  { code: "AGP", name: "Malaga", city: "Malaga", country: "Spain" },
  { code: "IBZ", name: "Ibiza", city: "Ibiza", country: "Spain" },
  { code: "VLC", name: "Valencia", city: "Valencia", country: "Spain" },
  { code: "SVQ", name: "Seville", city: "Seville", country: "Spain" },
  
  // France
  { code: "CDG", name: "Charles de Gaulle", city: "Paris", country: "France" },
  { code: "ORY", name: "Orly", city: "Paris", country: "France" },
  { code: "NCE", name: "Nice", city: "Nice", country: "France" },
  { code: "MRS", name: "Marseille", city: "Marseille", country: "France" },
  { code: "TLS", name: "Toulouse", city: "Toulouse", country: "France" },
  { code: "LYS", name: "Lyon", city: "Lyon", country: "France" },
  
  // Italy
  { code: "FCO", name: "Fiumicino", city: "Rome", country: "Italy" },
  { code: "MXP", name: "Malpensa", city: "Milan", country: "Italy" },
  { code: "VCE", name: "Marco Polo", city: "Venice", country: "Italy" },
  { code: "FLR", name: "Florence", city: "Florence", country: "Italy" },
  { code: "NAP", name: "Naples", city: "Naples", country: "Italy" },
  { code: "PSA", name: "Pisa", city: "Pisa", country: "Italy" },
  
  // Germany
  { code: "FRA", name: "Frankfurt", city: "Frankfurt", country: "Germany" },
  { code: "MUC", name: "Munich", city: "Munich", country: "Germany" },
  { code: "BER", name: "Berlin Brandenburg", city: "Berlin", country: "Germany" },
  { code: "DUS", name: "Dusseldorf", city: "Dusseldorf", country: "Germany" },
  { code: "CGN", name: "Cologne", city: "Cologne", country: "Germany" },
  
  // Netherlands
  { code: "AMS", name: "Schiphol", city: "Amsterdam", country: "Netherlands" },
  
  // Belgium
  { code: "BRU", name: "Brussels", city: "Brussels", country: "Belgium" },
  
  // Switzerland
  { code: "ZRH", name: "Zurich", city: "Zurich", country: "Switzerland" },
  { code: "GVA", name: "Geneva", city: "Geneva", country: "Switzerland" },
  
  // Austria
  { code: "VIE", name: "Vienna", city: "Vienna", country: "Austria" },
  
  // Portugal
  { code: "LIS", name: "Lisbon", city: "Lisbon", country: "Portugal" },
  { code: "OPO", name: "Porto", city: "Porto", country: "Portugal" },
  { code: "FAO", name: "Faro", city: "Faro", country: "Portugal" },
  
  // Greece
  { code: "ATH", name: "Athens", city: "Athens", country: "Greece" },
  { code: "HER", name: "Heraklion", city: "Heraklion", country: "Greece" },
  { code: "RHO", name: "Rhodes", city: "Rhodes", country: "Greece" },
  
  // Croatia
  { code: "DBV", name: "Dubrovnik", city: "Dubrovnik", country: "Croatia" },
  { code: "SPU", name: "Split", city: "Split", country: "Croatia" },
  { code: "ZAG", name: "Zagreb", city: "Zagreb", country: "Croatia" },
  
  // Poland
  { code: "WAW", name: "Warsaw", city: "Warsaw", country: "Poland" },
  { code: "KRK", name: "Krakow", city: "Krakow", country: "Poland" },
  
  // Czech Republic
  { code: "PRG", name: "Prague", city: "Prague", country: "Czech Republic" },
  
  // Hungary
  { code: "BUD", name: "Budapest", city: "Budapest", country: "Hungary" },
  
  // Ireland
  { code: "DUB", name: "Dublin", city: "Dublin", country: "Ireland" },
  { code: "SNN", name: "Shannon", city: "Shannon", country: "Ireland" },
  
  // Norway
  { code: "OSL", name: "Oslo", city: "Oslo", country: "Norway" },
  
  // Sweden
  { code: "ARN", name: "Arlanda", city: "Stockholm", country: "Sweden" },
  
  // Denmark
  { code: "CPH", name: "Copenhagen", city: "Copenhagen", country: "Denmark" },
  
  // Finland
  { code: "HEL", name: "Helsinki", city: "Helsinki", country: "Finland" }
];

// Helper function to get airport by code
export const getAirportByCode = (code: string): Airport | undefined => {
  return airports.find(airport => airport.code === code);
};

// Helper function to search airports by name or city
export const searchAirports = (query: string): Airport[] => {
  const lowerQuery = query.toLowerCase();
  return airports.filter(airport => 
    airport.name.toLowerCase().includes(lowerQuery) ||
    airport.city.toLowerCase().includes(lowerQuery) ||
    airport.code.toLowerCase().includes(lowerQuery) ||
    airport.country.toLowerCase().includes(lowerQuery)
  );
};
