<template>
  <div>
    <div :id="chartId" class="chart-viz"></div>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading airport data...</span>
    </div>
    <!-- Legend for bubble chart -->
    <div class="bubble-legend" v-if="!loading">
      <div class="legend-section">
        <span class="legend-title">Size = Total Flights</span>
        <div class="size-legend">
          <div class="size-item">
            <svg width="16" height="16"><circle cx="8" cy="8" r="4" fill="rgba(255,255,255,0.3)"/></svg>
            <span>Low</span>
          </div>
          <div class="size-item">
            <svg width="24" height="24"><circle cx="12" cy="12" r="8" fill="rgba(255,255,255,0.3)"/></svg>
            <span>Medium</span>
          </div>
          <div class="size-item">
            <svg width="40" height="40"><circle cx="20" cy="20" r="16" fill="rgba(255,255,255,0.3)"/></svg>
            <span>High</span>
          </div>
        </div>
      </div>
      <div class="legend-section">
        <span class="legend-title">Color = Dominant Delay Type</span>
        <div class="color-legend">
          <div v-for="(color, type) in delayTypeColors" :key="type" class="color-item">
            <div class="color-swatch" :style="{ backgroundColor: color }"></div>
            <span>{{ type }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import * as d3 from 'd3'
import { createTooltip, formatTooltip, formatNumber, formatMinutes, formatDecimal, delayColors, abbreviateNumber } from '@/utils/chartUtils'

export default {
  name: 'BubbleChart',
  props: {
    filters: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['airport-selected'],
  setup(props, { emit }) {
    const chartId = 'bubble-' + Math.random().toString(36).substr(2, 9)
    const loading = ref(true)
    let allData = []
    
    const delayTypeColors = {
      'Carrier': delayColors.carrier,
      'Weather': delayColors.weather,
      'NAS': delayColors.nas,
      'Security': delayColors.security,
      'Late Aircraft': delayColors.late_aircraft
    }

    const processData = async () => {
      try {
        const delays = await d3.csv('/Airline_Delay_Cause.csv')
        const airports = await d3.csv('/airports_geographic.csv')
        
        // Create airport mapping
        const airportMap = {}
        airports.forEach(row => {
          if (row.iata_code) {
            airportMap[row.iata_code] = {
              name: row.name || row.iata_code,
              state: row.iso_region ? row.iso_region.split('-')[1] : null,
              lat: +row.latitude_deg,
              lon: +row.longitude_deg
            }
          }
        })
        
        // Aggregate by airport
        const airportData = {}
        
        delays.forEach(row => {
          const airport = row.airport
          if (!airport) return
          
          const airportInfo = airportMap[airport]
          const state = airportInfo?.state || row.airport_state
          const carrier = row.carrier_name || row.carrier
          
          if (!airportData[airport]) {
            airportData[airport] = {
              airport_code: airport,
              airport_name: airportInfo?.name || airport,
              state: state,
              lat: airportInfo?.lat,
              lon: airportInfo?.lon,
              total_flights: 0,
              total_delay: 0,
              total_cancelled: 0,
              delayed_flights: 0,
              carriers: new Set(),
              delay_types: {
                carrier: 0,
                weather: 0,
                nas: 0,
                security: 0,
                late_aircraft: 0
              }
            }
          }
          
          const flights = +row.arr_flights || 0
          const delay = +row.arr_delay || 0
          const cancelled = +row.arr_cancelled || 0
          const delayed = +row.arr_del15 || 0
          
          airportData[airport].total_flights += flights
          airportData[airport].total_delay += delay
          airportData[airport].total_cancelled += cancelled
          airportData[airport].delayed_flights += delayed
          if (carrier) airportData[airport].carriers.add(carrier)
          airportData[airport].delay_types.carrier += (+row.carrier_delay || 0)
          airportData[airport].delay_types.weather += (+row.weather_delay || 0)
          airportData[airport].delay_types.nas += (+row.nas_delay || 0)
          airportData[airport].delay_types.security += (+row.security_delay || 0)
          airportData[airport].delay_types.late_aircraft += (+row.late_aircraft_delay || 0)
        })
        
        // Convert to array and calculate metrics
        let data = Object.values(airportData).map(d => {
          const delayTypes = d.delay_types
          const maxDelayType = Object.keys(delayTypes).reduce((a, b) => 
            delayTypes[a] > delayTypes[b] ? a : b
          )
          
          const delayTypeLabels = {
            carrier: 'Carrier',
            weather: 'Weather',
            nas: 'NAS',
            security: 'Security',
            late_aircraft: 'Late Aircraft'
          }
          
          return {
            ...d,
            avg_delay_min: d.total_flights > 0 ? d.total_delay / d.total_flights : 0,
            cancel_rate: d.total_flights > 0 ? (d.total_cancelled / d.total_flights) * 100 : 0,
            delay_rate: d.total_flights > 0 ? (d.delayed_flights / d.total_flights) * 100 : 0,
            dominant_delay_type: maxDelayType,
            dominant_delay_label: delayTypeLabels[maxDelayType],
            carriers: Array.from(d.carriers)
          }
        })
        
        // Sort by flights and take top 60 for better visualization
        return data.sort((a, b) => b.total_flights - a.total_flights).slice(0, 60)
      } catch (err) {
        console.error('Error processing bubble chart data:', err)
        throw err
      }
    }

    const drawChart = async (animate = true) => {
      try {
        loading.value = true
        
        // Load data only once
        if (allData.length === 0) {
          allData = await processData()
        }
        
        // Apply filters
        let data = [...allData]
        
        if (props.filters.selectedState) {
          data = data.filter(d => d.state === props.filters.selectedState)
        }
        
        if (props.filters.selectedCarrier) {
          data = data.filter(d => d.carriers.includes(props.filters.selectedCarrier))
        }
        
        // If no data after filtering, show message
        if (data.length === 0) {
          d3.select(`#${chartId}`).selectAll('*').remove()
          d3.select(`#${chartId}`)
            .append('div')
            .attr('class', 'no-data-message')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('justify-content', 'center')
            .style('height', '400px')
            .style('color', 'var(--text-secondary)')
            .style('font-size', '1.1rem')
            .text('No airports match the current filters')
          loading.value = false
          return
        }
        
        d3.select(`#${chartId}`).selectAll('*').remove()
        
        const container = document.getElementById(chartId)
        const margin = { top: 30, right: 40, bottom: 60, left: 70 }
        const width = (container?.clientWidth || 600) - margin.left - margin.right
        const height = 350 - margin.top - margin.bottom
        
        const svg = d3.select(`#${chartId}`)
          .append('svg')
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)
          .append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`)
        
        // X Scale: Log scale for total flights
        const xExtent = d3.extent(data, d => d.total_flights)
        const xScale = d3.scaleLog()
          .domain([Math.max(1, xExtent[0] * 0.9), xExtent[1] * 1.1])
          .range([0, width])
        
        // Y Scale: Linear for average delay
        const yMax = d3.max(data, d => d.avg_delay_min)
        const yScale = d3.scaleLinear()
          .domain([0, yMax * 1.1])
          .range([height, 0])
          .nice()
        
        // Size Scale: Square root for total flights (area perception)
        const sizeScale = d3.scaleSqrt()
          .domain([0, d3.max(data, d => d.total_flights)])
          .range([5, 45])
        
        // Color Scale: By dominant delay type
        const colorScale = d3.scaleOrdinal()
          .domain(['carrier', 'weather', 'nas', 'security', 'late_aircraft'])
          .range([
            delayColors.carrier,
            delayColors.weather,
            delayColors.nas,
            delayColors.security,
            delayColors.late_aircraft
          ])
        
        const tooltip = createTooltip(chartId)
        
        // Add grid lines
        svg.append('g')
          .attr('class', 'grid-lines')
          .selectAll('line.horizontal')
          .data(yScale.ticks(6))
          .enter()
          .append('line')
          .attr('class', 'horizontal')
          .attr('x1', 0)
          .attr('x2', width)
          .attr('y1', d => yScale(d))
          .attr('y2', d => yScale(d))
          .attr('stroke', 'rgba(255,255,255,0.05)')
          .attr('stroke-dasharray', '3,3')
        
        // Draw bubbles
        const bubbles = svg.selectAll('.bubble')
          .data(data, d => d.airport_code)
          .enter()
          .append('circle')
          .attr('class', 'bubble')
          .attr('cx', d => xScale(d.total_flights))
          .attr('cy', d => yScale(d.avg_delay_min))
          .attr('r', 0)
          .attr('fill', d => colorScale(d.dominant_delay_type))
          .attr('stroke', d => {
            if (props.filters.selectedAirport === d.airport_code) {
              return '#fff'
            }
            return 'rgba(255,255,255,0.3)'
          })
          .attr('stroke-width', d => props.filters.selectedAirport === d.airport_code ? 3 : 1.5)
          .attr('opacity', d => {
            if (props.filters.selectedAirport && props.filters.selectedAirport !== d.airport_code) {
              return 0.3
            }
            return 0.75
          })
          .style('cursor', 'pointer')
          .on('mouseover', function(event, d) {
            // Highlight this bubble
            d3.select(this)
              .attr('opacity', 1)
              .attr('stroke', '#fff')
              .attr('stroke-width', 3)
            
            // Dim other bubbles
            d3.selectAll('.bubble')
              .filter(node => node !== d)
              .attr('opacity', 0.25)
            
            const html = formatTooltip(
              `${d.airport_code} - ${d.airport_name}`,
              {
                'State': d.state,
                'Total Flights': abbreviateNumber(d.total_flights),
                'Avg Delay': formatMinutes(d.avg_delay_min),
                'Delay Rate': formatDecimal(d.delay_rate) + '%',
                'Cancel Rate': formatDecimal(d.cancel_rate) + '%',
                'Cancellations': formatNumber(d.total_cancelled),
                'Primary Delay': d.dominant_delay_label
              },
              { highlightColor: colorScale(d.dominant_delay_type) }
            )
            tooltip.show(html, event)
          })
          .on('mousemove', function(event) {
            tooltip.move(event)
          })
          .on('mouseout', function(event, d) {
            // Reset all bubbles
            d3.selectAll('.bubble')
              .attr('opacity', bubble => {
                if (props.filters.selectedAirport && props.filters.selectedAirport !== bubble.airport_code) {
                  return 0.3
                }
                return 0.75
              })
              .attr('stroke', bubble => {
                if (props.filters.selectedAirport === bubble.airport_code) {
                  return '#fff'
                }
                return 'rgba(255,255,255,0.3)'
              })
              .attr('stroke-width', bubble => props.filters.selectedAirport === bubble.airport_code ? 3 : 1.5)
            
            tooltip.hide()
          })
          .on('click', function(event, d) {
            const isSelected = props.filters.selectedAirport === d.airport_code
            emit('airport-selected', isSelected ? null : d.airport_code)
          })
        
        // Animate bubble appearance
        if (animate) {
          bubbles.transition()
            .duration(800)
            .delay((d, i) => i * 15)
            .attr('r', d => sizeScale(d.total_flights))
        } else {
          bubbles.attr('r', d => sizeScale(d.total_flights))
        }
        
        // Add airport labels for selected or top airports
        const labelData = data.slice(0, 8) // Top 8 airports
        svg.selectAll('.airport-label')
          .data(labelData)
          .enter()
          .append('text')
          .attr('class', 'airport-label')
          .attr('x', d => xScale(d.total_flights))
          .attr('y', d => yScale(d.avg_delay_min) - sizeScale(d.total_flights) - 8)
          .attr('text-anchor', 'middle')
          .attr('fill', 'var(--text-secondary)')
          .attr('font-size', '0.7rem')
          .attr('font-weight', '600')
          .text(d => d.airport_code)
          .style('pointer-events', 'none')
          .style('opacity', 0)
          .transition()
          .delay(1000)
          .duration(400)
          .style('opacity', 1)
        
        // X Axis
        const xAxis = svg.append('g')
          .attr('transform', `translate(0,${height})`)
          .call(d3.axisBottom(xScale)
            .ticks(5)
            .tickFormat(d => abbreviateNumber(d)))
        
        xAxis.selectAll('text')
          .attr('fill', 'var(--text-secondary)')
        xAxis.selectAll('line, path')
          .attr('stroke', 'var(--border-color)')
        
        svg.append('text')
          .attr('x', width / 2)
          .attr('y', height + 45)
          .attr('text-anchor', 'middle')
          .style('font-weight', '600')
          .style('font-size', '0.85rem')
          .style('fill', 'var(--text-secondary)')
          .text('Total Flights (Log Scale)')
        
        // Y Axis
        const yAxis = svg.append('g')
          .call(d3.axisLeft(yScale).ticks(6))
        
        yAxis.selectAll('text')
          .attr('fill', 'var(--text-secondary)')
        yAxis.selectAll('line, path')
          .attr('stroke', 'var(--border-color)')
        
        svg.append('text')
          .attr('transform', 'rotate(-90)')
          .attr('y', -50)
          .attr('x', -height / 2)
          .attr('text-anchor', 'middle')
          .style('font-weight', '600')
          .style('font-size', '0.85rem')
          .style('fill', 'var(--text-secondary)')
          .text('Average Delay (minutes)')
        
        loading.value = false
      } catch (err) {
        console.error('Error drawing bubble chart:', err)
        loading.value = false
      }
    }

    // Watch for filter changes
    watch(() => props.filters, () => {
      drawChart(false)
    }, { deep: true })

    onMounted(() => drawChart(true))

    return { chartId, loading, delayTypeColors }
  }
}
</script>

<style scoped>
.chart-viz {
  width: 100%;
  min-height: 350px;
  position: relative;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 350px;
  gap: 15px;
}

.bubble-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid var(--border-color);
}

.legend-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.size-legend {
  display: flex;
  align-items: flex-end;
  gap: 15px;
}

.size-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.color-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.color-swatch {
  width: 14px;
  height: 14px;
  border-radius: 3px;
}

:deep(.bubble) {
  transition: opacity 0.2s, stroke 0.2s, stroke-width 0.2s;
}

:deep(.bubble.selected) {
  stroke: #fff !important;
  stroke-width: 3 !important;
}
</style>
