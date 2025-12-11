// airlineCountries.js - Mapping of airlines to their countries
export const airlineCountries = {
    // US Airlines
    'American Airlines': 'USA',
    'Delta Air Lines': 'USA',
    'United Airlines': 'USA',
    'Southwest Airlines': 'USA',
    'JetBlue Airways': 'USA',
    'Alaska Airlines': 'USA',
    'Spirit Airlines': 'USA',
    'Frontier Airlines': 'USA',
    'Hawaiian Airlines': 'USA',
    'Allegiant Air': 'USA',
    
    // European Airlines
    'Lufthansa': 'Germany',
    'British Airways': 'UK',
    'Air France': 'France',
    'KLM': 'Netherlands',
    'Ryanair': 'Ireland',
    'EasyJet': 'UK',
    'Turkish Airlines': 'Turkey',
    'Alitalia': 'Italy',
    'Iberia': 'Spain',
    'Swiss': 'Switzerland',
    'Austrian Airlines': 'Austria',
    
    // Asian Airlines
    'Singapore Airlines': 'Singapore',
    'Cathay Pacific': 'Hong Kong',
    'Japan Airlines': 'Japan',
    'ANA': 'Japan',
    'Korean Air': 'South Korea',
    'Thai Airways': 'Thailand',
    'Emirates': 'UAE',
    'Qatar Airways': 'Qatar',
    'Etihad Airways': 'UAE',
    
    // Canadian Airlines
    'Air Canada': 'Canada',
    'WestJet': 'Canada',
    
    // Latin American Airlines
    'LATAM': 'Chile',
    'Avianca': 'Colombia',
    'Copa Airlines': 'Panama',
    'Aeromexico': 'Mexico',
    
    // Other
    'Qantas': 'Australia',
    'Air New Zealand': 'New Zealand'
  }
  
  // Get country for airline (fuzzy matching)
  export function getAirlineCountry(airlineName) {
    if (!airlineName) return 'Unknown'
    
    const normalized = airlineName.toLowerCase().trim()
    
    // Direct match
    for (const [airline, country] of Object.entries(airlineCountries)) {
      if (airline.toLowerCase() === normalized) {
        return country
      }
    }
    
    // Partial match
    for (const [airline, country] of Object.entries(airlineCountries)) {
      if (normalized.includes(airline.toLowerCase()) || airline.toLowerCase().includes(normalized)) {
        return country
      }
    }
    
    return 'Unknown'
  }
  
  // Get all unique countries
  export function getAllCountries() {
    const countries = new Set(Object.values(airlineCountries))
    return Array.from(countries).sort()
  }
  
  // Get airlines by country
  export function getAirlinesByCountry(country) {
    return Object.entries(airlineCountries)
      .filter(([_, c]) => c === country)
      .map(([airline, _]) => airline)
  }
  
  // Country regions for grouping
  export const countryRegions = {
    'USA': 'North America',
    'Canada': 'North America',
    'Mexico': 'North America',
    
    'UK': 'Europe',
    'Germany': 'Europe',
    'France': 'Europe',
    'Netherlands': 'Europe',
    'Ireland': 'Europe',
    'Turkey': 'Europe',
    'Italy': 'Europe',
    'Spain': 'Europe',
    'Switzerland': 'Europe',
    'Austria': 'Europe',
    
    'Singapore': 'Asia',
    'Hong Kong': 'Asia',
    'Japan': 'Asia',
    'South Korea': 'Asia',
    'Thailand': 'Asia',
    'UAE': 'Middle East',
    'Qatar': 'Middle East',
    
    'Chile': 'Latin America',
    'Colombia': 'Latin America',
    'Panama': 'Latin America',
    
    'Australia': 'Oceania',
    'New Zealand': 'Oceania'
  }
  
  export function getCountryRegion(country) {
    return countryRegions[country] || 'Other'
  }