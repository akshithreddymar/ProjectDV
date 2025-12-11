import * as d3 from 'd3'

// Color schemes for delay types (adjusted for light theme)
export const delayColors = {
  'carrier': '#ef4444',
  'weather': '#3b82f6',
  'nas': '#f59e0b',
  'security': '#a855f7',
  'late_aircraft': '#14b8a6',
  'Carrier': '#ef4444',
  'Weather': '#3b82f6',
  'NAS': '#f59e0b',
  'Security': '#a855f7',
  'Late Aircraft': '#14b8a6'
}

// Airline colors for parallel coordinates (light theme optimized)
export const airlineColors = [
  '#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#06b6d4',
  '#84cc16', '#f43f5e', '#0ea5e9', '#a855f7', '#eab308'
]

// Performance tier colors
export const performanceTiers = {
  'excellent': '#22c55e',
  'good': '#10b981',
  'average': '#f59e0b',
  'poor': '#f97316',
  'critical': '#ef4444'
}

// Sentiment colors for reviews
export const sentimentColors = {
  'positive': '#22c55e',
  'neutral': '#f59e0b',
  'negative': '#ef4444'
}

// Rating colors
export const ratingColors = d3.scaleSequential()
  .domain([0, 10])
  .interpolator(d3.interpolateRdYlGn)

// Number formatting utilities
export const formatNumber = d3.format(',')
export const formatDecimal = d3.format(',.2f')
export const formatPercent = d3.format('.1%')
export const formatPercentRaw = d3.format('.1f')

export function abbreviateNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

export function formatMinutes(mins) {
  if (mins < 60) {
    return `${Math.round(mins)}m`
  }
  const hours = Math.floor(mins / 60)
  const minutes = Math.round(mins % 60)
  return `${hours}h ${minutes}m`
}

// Enhanced tooltip helper with better positioning for light theme
export function createTooltip(containerId) {
  const container = d3.select(`#${containerId}`)
  
  let tooltip = container.select('.d3-tooltip')
  if (tooltip.empty()) {
    tooltip = container.append('div')
      .attr('class', 'd3-tooltip')
      .style('position', 'absolute')
      .style('background', 'rgba(15, 23, 42, 0.96)')
      .style('color', 'white')
      .style('padding', '12px 16px')
      .style('border-radius', '10px')
      .style('font-size', '0.85rem')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('z-index', 1000)
      .style('max-width', '300px')
      .style('box-shadow', '0 8px 24px rgba(0,0,0,0.25)')
      .style('border', '1px solid rgba(255,255,255,0.1)')
      .style('backdrop-filter', 'blur(10px)')
      .style('transition', 'opacity 0.15s ease')
      .style('font-family', 'Inter, sans-serif')
  }
  
  return {
    show(html, event) {
      const containerRect = container.node().getBoundingClientRect()
      let offsetX = event.clientX - containerRect.left + 15
      let offsetY = event.clientY - containerRect.top - 10
      
      // Adjust position if tooltip would go off-screen
      const tooltipNode = tooltip.node()
      if (tooltipNode) {
        const tooltipRect = tooltipNode.getBoundingClientRect()
        if (offsetX + tooltipRect.width > containerRect.width) {
          offsetX = event.clientX - containerRect.left - tooltipRect.width - 15
        }
        if (offsetY + tooltipRect.height > containerRect.height) {
          offsetY = event.clientY - containerRect.top - tooltipRect.height - 10
        }
      }
      
      tooltip
        .html(html)
        .style('opacity', 1)
        .style('left', offsetX + 'px')
        .style('top', offsetY + 'px')
    },
    hide() {
      tooltip.style('opacity', 0)
    },
    move(event) {
      const containerRect = container.node().getBoundingClientRect()
      let offsetX = event.clientX - containerRect.left + 15
      let offsetY = event.clientY - containerRect.top - 10
      
      tooltip
        .style('left', offsetX + 'px')
        .style('top', offsetY + 'px')
    }
  }
}

// Create enhanced tooltip HTML with styling
export function formatTooltip(title, data, options = {}) {
  const { highlightColor = '#3b82f6', showIcon = false, icon = '' } = options
  
  let html = `
    <div style="font-weight: 700; margin-bottom: 10px; border-bottom: 2px solid ${highlightColor}; padding-bottom: 8px; font-size: 0.95rem;">
      ${showIcon ? icon + ' ' : ''}${title}
    </div>
  `
  
  for (const [label, value] of Object.entries(data)) {
    html += `
      <div style="display: flex; justify-content: space-between; margin: 6px 0; gap: 15px;">
        <span style="opacity: 0.85; font-size: 0.8rem;">${label}:</span>
        <span style="font-weight: 600; color: #fff;">${value}</span>
      </div>
    `
  }
  
  return html
}

// FIPS code to state code mapping
export const fipsToState = {
  '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA',
  '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL',
  '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN',
  '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME',
  '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS',
  '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
  '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND',
  '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
  '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT',
  '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI',
  '56': 'WY'
}

// State code to FIPS mapping (reverse)
export const stateToFips = Object.fromEntries(
  Object.entries(fipsToState).map(([k, v]) => [v, k])
)

// State full names
export const stateNames = {
  'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
  'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
  'DC': 'Washington DC', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
  'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
  'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
  'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
  'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska',
  'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
  'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
  'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
  'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
  'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
  'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

// Debounce utility for performance
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Throttle utility for mousemove events
export function throttle(func, limit) {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// Statistical utilities
export function calculateMean(values) {
  return values.length > 0 ? d3.mean(values) : 0
}

export function calculateMedian(values) {
  return values.length > 0 ? d3.median(values) : 0
}

export function calculateStdDev(values) {
  return values.length > 0 ? d3.deviation(values) : 0
}

export function calculateCorrelation(x, y) {
  if (x.length !== y.length || x.length === 0) return 0
  
  const n = x.length
  const meanX = d3.mean(x)
  const meanY = d3.mean(y)
  
  let numerator = 0
  let denomX = 0
  let denomY = 0
  
  for (let i = 0; i < n; i++) {
    const dx = x[i] - meanX
    const dy = y[i] - meanY
    numerator += dx * dy
    denomX += dx * dx
    denomY += dy * dy
  }
  
  if (denomX === 0 || denomY === 0) return 0
  return numerator / Math.sqrt(denomX * denomY)
}

// Parse Skytrax review date
export function parseReviewDate(dateStr) {
  // Format is like "2015-04-10"
  const date = new Date(dateStr)
  return date
}

// Get sentiment from rating
export function getSentiment(rating) {
  if (rating >= 7) return 'positive'
  if (rating >= 4) return 'neutral'
  return 'negative'
}

// Calculate recommendation percentage
export function calculateRecommendationRate(reviews) {
  const total = reviews.length
  const recommended = reviews.filter(r => r.recommended === '1' || r.recommended === 1).length
  return total > 0 ? (recommended / total) * 100 : 0
}

// Aggregate reviews by airline
export function aggregateReviewsByAirline(reviews) {
  const airlines = {}
  
  reviews.forEach(review => {
    const airline = review.airline_name
    if (!airline) return
    
    if (!airlines[airline]) {
      airlines[airline] = {
        name: airline,
        count: 0,
        totalRating: 0,
        recommended: 0,
        ratings: {
          overall: [],
          seat_comfort: [],
          cabin_staff: [],
          food_beverages: [],
          value_money: []
        }
      }
    }
    
    airlines[airline].count++
    
    const overallRating = parseFloat(review.overall_rating)
    if (!isNaN(overallRating)) {
      airlines[airline].totalRating += overallRating
      airlines[airline].ratings.overall.push(overallRating)
    }
    
    if (review.recommended === '1' || review.recommended === 1) {
      airlines[airline].recommended++
    }
    
    // Collect other ratings
    const seatComfort = parseFloat(review.seat_comfort_rating)
    if (!isNaN(seatComfort) && seatComfort > 0) {
      airlines[airline].ratings.seat_comfort.push(seatComfort)
    }
    
    const cabinStaff = parseFloat(review.cabin_staff_rating)
    if (!isNaN(cabinStaff) && cabinStaff > 0) {
      airlines[airline].ratings.cabin_staff.push(cabinStaff)
    }
    
    const foodBev = parseFloat(review.food_beverages_rating)
    if (!isNaN(foodBev) && foodBev > 0) {
      airlines[airline].ratings.food_beverages.push(foodBev)
    }
    
    const valueMoney = parseFloat(review.value_money_rating)
    if (!isNaN(valueMoney) && valueMoney > 0) {
      airlines[airline].ratings.value_money.push(valueMoney)
    }
  })
  
  // Calculate averages
  Object.values(airlines).forEach(airline => {
    airline.avgRating = airline.count > 0 ? airline.totalRating / airline.count : 0
    airline.recommendationRate = airline.count > 0 ? (airline.recommended / airline.count) * 100 : 0
    
    // Calculate average for each rating dimension
    Object.keys(airline.ratings).forEach(key => {
      if (airline.ratings[key].length > 0) {
        airline.ratings[key + '_avg'] = d3.mean(airline.ratings[key])
      } else {
        airline.ratings[key + '_avg'] = 0
      }
    })
  })
  
  return Object.values(airlines)
}