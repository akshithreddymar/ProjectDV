import * as d3 from 'd3'

// Color schemes for delay types
export const delayColors = {
  'carrier': '#e74c3c',
  'weather': '#3498db',
  'nas': '#f39c12',
  'security': '#9b59b6',
  'late_aircraft': '#1abc9c',
  'Carrier': '#e74c3c',
  'Weather': '#3498db',
  'NAS': '#f39c12',
  'Security': '#9b59b6',
  'Late Aircraft': '#1abc9c'
}

// Airline colors for parallel coordinates
export const airlineColors = [
  '#667eea', '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
  '#9b59b6', '#1abc9c', '#e67e22', '#34495e', '#16a085',
  '#c0392b', '#2980b9', '#27ae60', '#8e44ad', '#d35400'
]

// Performance tier colors
export const performanceTiers = {
  'excellent': '#27ae60',
  'good': '#2ecc71',
  'average': '#f39c12',
  'poor': '#e67e22',
  'critical': '#e74c3c'
}

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

// Enhanced tooltip helper with better positioning
export function createTooltip(containerId) {
  const container = d3.select(`#${containerId}`)
  
  let tooltip = container.select('.d3-tooltip')
  if (tooltip.empty()) {
    tooltip = container.append('div')
      .attr('class', 'd3-tooltip')
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.92)')
      .style('color', 'white')
      .style('padding', '14px 18px')
      .style('border-radius', '10px')
      .style('font-size', '0.85rem')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('z-index', 1000)
      .style('max-width', '280px')
      .style('box-shadow', '0 8px 24px rgba(0,0,0,0.4)')
      .style('border', '1px solid rgba(255,255,255,0.1)')
      .style('backdrop-filter', 'blur(10px)')
      .style('transition', 'opacity 0.15s ease')
  }
  
  return {
    show(html, event) {
      const containerRect = container.node().getBoundingClientRect()
      const offsetX = event.clientX - containerRect.left + 15
      const offsetY = event.clientY - containerRect.top - 10
      
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
      const offsetX = event.clientX - containerRect.left + 15
      const offsetY = event.clientY - containerRect.top - 10
      
      tooltip
        .style('left', offsetX + 'px')
        .style('top', offsetY + 'px')
    }
  }
}

// Create enhanced tooltip HTML with styling
export function formatTooltip(title, data, options = {}) {
  const { highlightColor = '#667eea', showIcon = false, icon = '' } = options
  
  let html = `
    <div style="font-weight: 700; margin-bottom: 10px; border-bottom: 2px solid ${highlightColor}; padding-bottom: 8px; font-size: 0.95rem;">
      ${showIcon ? icon + ' ' : ''}${title}
    </div>
  `
  
  for (const [label, value] of Object.entries(data)) {
    html += `
      <div style="display: flex; justify-content: space-between; margin: 6px 0; gap: 15px;">
        <span style="opacity: 0.75; font-size: 0.8rem;">${label}:</span>
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
