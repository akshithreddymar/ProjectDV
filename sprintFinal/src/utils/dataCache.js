// dataCache.js - Centralized data loading and caching
import * as d3 from 'd3'

// Cache for loaded data
let dataCache = {
  delays: null,
  reviews: null,
  airports: null,
  loading: false,
  promise: null
}

// Load all data once and cache it
export async function loadAllData() {
  // If already loading, return the existing promise
  if (dataCache.loading && dataCache.promise) {
    return dataCache.promise
  }

  // If data is already cached, return it immediately
  if (dataCache.delays && dataCache.reviews) {
    return {
      delays: dataCache.delays,
      reviews: dataCache.reviews,
      airports: dataCache.airports
    }
  }

  // Set loading flag
  dataCache.loading = true

  // Create promise for data loading
  dataCache.promise = Promise.all([
    d3.csv('/Airline_Delay_Cause.csv'),
    d3.csv('/skytrax_airline_reviews.csv'),
    d3.csv('/airports_geographic.csv').catch(() => null) // Optional
  ])
    .then(([delays, reviews, airports]) => {
      // Cache the data
      dataCache.delays = delays
      dataCache.reviews = reviews
      dataCache.airports = airports
      dataCache.loading = false

      return {
        delays,
        reviews,
        airports
      }
    })
    .catch(error => {
      dataCache.loading = false
      throw error
    })

  return dataCache.promise
}

// Get cached data or load if not available
export async function getCachedData() {
  return loadAllData()
}

// Clear cache (useful for testing or forced refresh)
export function clearDataCache() {
  dataCache = {
    delays: null,
    reviews: null,
    airports: null,
    loading: false,
    promise: null
  }
}

// Filter delay data based on common filters
export function filterDelayData(delays, filters = {}) {
  return delays.filter(row => {
    const year = +row.year
    
    // Year range filter
    if (filters.yearStart && filters.yearEnd) {
      if (year < filters.yearStart || year > filters.yearEnd) return false
    }
    
    // Carrier filter
    if (filters.selectedCarrier && row.carrier_name !== filters.selectedCarrier) {
      return false
    }
    
    // Airport filter
    if (filters.selectedAirport && row.airport !== filters.selectedAirport) {
      return false
    }
    
    // State filter
    if (filters.selectedState && row.state !== filters.selectedState) {
      return false
    }
    
    // Delay type filter (if needed)
    if (filters.selectedDelayType) {
      // Check if this row has significant delays of the selected type
      const delayType = filters.selectedDelayType.toLowerCase().replace(/\s+/g, '_')
      const delayCount = +(row[`${delayType}_ct`] || 0)
      if (delayCount === 0) return false
    }
    
    return true
  })
}

// Filter review data based on common filters
export function filterReviewData(reviews, filters = {}) {
  return reviews.filter(row => {
    const date = new Date(row.date)
    const year = date.getFullYear()
    
    // Date range filter (2015-2025)
    if (year < 2015 || year > 2025) return false
    
    // Year range filter
    if (filters.yearStart && filters.yearEnd) {
      if (year < filters.yearStart || year > filters.yearEnd) return false
    }
    
    // Carrier/Airline filter (fuzzy match since names might differ)
    if (filters.selectedCarrier) {
      const reviewAirline = (row.airline_name || '').toLowerCase().trim()
      const filterCarrier = filters.selectedCarrier.toLowerCase().trim()
      
      // Check if airline name contains carrier or vice versa
      if (!reviewAirline.includes(filterCarrier) && !filterCarrier.includes(reviewAirline)) {
        // Try partial matching
        const reviewWords = reviewAirline.split(/\s+/)
        const filterWords = filterCarrier.split(/\s+/)
        
        const hasMatch = reviewWords.some(rw => 
          filterWords.some(fw => rw.includes(fw) || fw.includes(rw))
        )
        
        if (!hasMatch) return false
      }
    }
    
    return true
  })
}

// Preload data on app initialization
export function preloadData() {
  loadAllData().catch(error => {
    console.error('Failed to preload data:', error)
  })
}