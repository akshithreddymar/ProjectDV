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

// Tooltip helper
export function createTooltip(containerId) {
  const container = d3.select(`#${containerId}`)
  
  let tooltip = container.select('.d3-tooltip')
  if (tooltip.empty()) {
    tooltip = container.append('div')
      .attr('class', 'd3-tooltip')
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.9)')
      .style('color', 'white')
      .style('padding', '12px 16px')
      .style('border-radius', '8px')
      .style('font-size', '0.85rem')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('z-index', 1000)
      .style('max-width', '250px')
      .style('box-shadow', '0 4px 12px rgba(0,0,0,0.3)')
  }
  
  return {
    show(html, event) {
      tooltip
        .html(html)
        .style('opacity', 1)
        .style('left', (event.pageX + 15) + 'px')
        .style('top', (event.pageY - 28) + 'px')
    },
    hide() {
      tooltip.style('opacity', 0)
    }
  }
}

// Create tooltip HTML
export function formatTooltip(title, data) {
  let html = `<div style="font-weight: 600; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 6px;">${title}</div>`
  
  for (const [label, value] of Object.entries(data)) {
    html += `
      <div style="display: flex; justify-content: space-between; margin: 4px 0;">
        <span style="opacity: 0.8;">${label}:</span>
        <span style="font-weight: 600; margin-left: 10px;">${value}</span>
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