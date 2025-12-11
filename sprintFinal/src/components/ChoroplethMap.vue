<template>
  <div class="map-container">
    <div class="map-controls" v-if="!loading && !error">
      <button class="control-btn" @click="resetZoom" title="Reset Zoom">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
          <path d="M8 3.5c-2.5 0-4.5 2-4.5 4.5s2 4.5 4.5 4.5 4.5-2 4.5-4.5-2-4.5-4.5-4.5zm0-1.5c3.3 0 6 2.7 6 6s-2.7 6-6 6-6-2.7-6-6 2.7-6 6-6z"/>
        </svg>
        Reset
      </button>
    </div>
    <div :id="chartId" class="chart-viz"></div>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading map data...</span>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div class="legend" v-if="!loading && !error">
      <div class="legend-title">Average Delay</div>
      <div v-for="(item, idx) in legendData" :key="idx" class="legend-item">
        <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
        <span>{{ item.label }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import { 
  createTooltip, 
  formatTooltip,
  formatNumber,
  formatDecimal,
  formatMinutes,
  fipsToState,
  stateNames,
  debounce
} from '@/utils/chartUtils'

export default {
  name: 'ChoroplethMap',
  props: {
    filters: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['state-selected'],
  setup(props, { emit }) {
    const chartId = 'choropleth-map-' + Math.random().toString(36).substr(2, 9)
    const loading = ref(true)
    const error = ref(null)
    const legendData = ref([])
    let svg, g, tooltip, stateData, colorScale, zoom, projection, path

    const processData = async () => {
      try {
        const delays = await d3.csv('/Airline_Delay_Cause.csv')
        const airports = await d3.csv('/airports_geographic.csv')

        const { yearStart, yearEnd, selectedCarrier, selectedAirport } = props.filters || {}
        
        // Create airport to state mapping
        const airportToState = {}
        airports.forEach(row => {
          if (row.iata_code && row.iso_region) {
            const state = row.iso_region.split('-')[1]
            airportToState[row.iata_code] = state
          }
        })
        
        // Aggregate by state
        const stateMap = {}
        
        delays.forEach(row => {
          const airport = row.airport
          const state = airportToState[airport] || row.airport_state
          if (!state) return

          const year = +row.year || null
          const carrierName = row.carrier_name || row.carrier

          // Apply ALL filters
          if (yearStart != null && yearEnd != null && year) {
            if (year < yearStart || year > yearEnd) return
          }

          if (selectedCarrier && carrierName && carrierName !== selectedCarrier) return
          if (selectedAirport && airport !== selectedAirport) return
          
          const carrier = carrierName
          
          if (!stateMap[state]) {
            stateMap[state] = {
              total_flights: 0,
              total_delay_minutes: 0,
              delayed_flights: 0,
              total_cancelled: 0,
              airports: new Set(),
              carriers: new Set()
            }
          }
          
          const flights = +row.arr_flights || 0
          const arrDelay = +row.arr_delay || 0
          const cancelled = +row.arr_cancelled || 0
          const delayed = +row.arr_del15 || 0
          
          stateMap[state].total_flights += flights
          stateMap[state].total_delay_minutes += arrDelay
          stateMap[state].delayed_flights += delayed
          stateMap[state].total_cancelled += cancelled
          if (airport) stateMap[state].airports.add(airport)
          if (carrier) stateMap[state].carriers.add(carrier)
        })
        
        // Calculate final metrics
        const processedData = {}
        Object.keys(stateMap).forEach(state => {
          const data = stateMap[state]
          processedData[state] = {
            total_flights: data.total_flights,
            avg_delay: data.total_flights > 0 ? data.total_delay_minutes / data.total_flights : 0,
            delay_rate: data.total_flights > 0 ? (data.delayed_flights / data.total_flights) * 100 : 0,
            cancel_rate: data.total_flights > 0 ? (data.total_cancelled / data.total_flights) * 100 : 0,
            airport_count: data.airports.size,
            carrier_count: data.carriers.size
          }
        })
        
        return processedData
      } catch (err) {
        console.error('Error processing data:', err)
        throw err
      }
    }

    const resetZoom = () => {
      if (svg && zoom) {
        svg.transition()
          .duration(750)
          .call(zoom.transform, d3.zoomIdentity)
      }
    }

    const drawMap = async () => {
      try {
        loading.value = true
        
        const [us, processedStateData] = await Promise.all([
          d3.json('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json'),
          processData()
        ])
        
        stateData = processedStateData
        
        d3.select(`#${chartId}`).selectAll('*').remove()
        
        const container = document.getElementById(chartId)
        const width = container?.clientWidth || 800
        const height = Math.max(400, width * 0.6)
        
        const svgElement = d3.select(`#${chartId}`)
          .append('svg')
          .attr('width', width)
          .attr('height', height)
          .style('background', '#f8fafc')
        
        svg = svgElement
        
        projection = d3.geoAlbersUsa()
          .translate([width / 2, height / 2])
          .scale(width * 1.1)
        
        path = d3.geoPath().projection(projection)
        
        // Color scale - light theme friendly
        const delayValues = Object.values(stateData).map(d => d.delay_rate)
        const min = d3.min(delayValues) || 0
        const max = d3.max(delayValues) || 100
        const mid = (min + max) / 2

        colorScale = d3.scaleSequential()
          .domain([min, max])
          .interpolator(d3.interpolateReds)
        
        legendData.value = [
          { label: `Low (${formatDecimal(min)}%)`, color: colorScale(min) },
          { label: `Medium (${formatDecimal(mid)}%)`, color: colorScale(mid) },
          { label: `High (${formatDecimal(max)}%)`, color: colorScale(max) }
        ]
        
        tooltip = createTooltip(chartId)
        
        const statesGeo = topojson.feature(us, us.objects.states)
        
        // Create group for zoom
        g = svgElement.append('g')
        
        // Setup zoom behavior
        zoom = d3.zoom()
          .scaleExtent([1, 8])
          .on('zoom', (event) => {
            g.attr('transform', event.transform)
          })
        
        svgElement.call(zoom)
        
        // Draw states
        g.selectAll('.state')
          .data(statesGeo.features)
          .enter()
          .append('path')
          .attr('class', 'state')
          .attr('d', path)
          .attr('fill', d => {
            const stateCode = fipsToState[d.id]
            const data = stateData[stateCode]
            if (!data || data.total_flights === 0) return '#e2e8f0'
            return colorScale(data.delay_rate)
          })
          .attr('stroke', d => {
            const stateCode = fipsToState[d.id]
            return props.filters.selectedState === stateCode ? '#3b82f6' : '#cbd5e1'
          })
          .attr('stroke-width', d => {
            const stateCode = fipsToState[d.id]
            return props.filters.selectedState === stateCode ? 3 : 0.8
          })
          .style('cursor', 'pointer')
          .on('mouseover', function(event, d) {
            const stateCode = fipsToState[d.id]
            const data = stateData[stateCode]
            
            if (!data || data.total_flights === 0) {
              tooltip.show(
                `<div style="font-weight: 700;">${stateNames[stateCode] || stateCode}</div>
                <div style="margin-top: 8px; color: #94a3b8;">No data available</div>`,
                event
              )
              return
            }
            
            d3.select(this)
              .attr('stroke', '#0f172a')
              .attr('stroke-width', 2)
            
            const tooltipHtml = formatTooltip(
              stateNames[stateCode] || stateCode,
              {
                'Delay Rate': `${data.delay_rate.toFixed(1)}%`,
                'Avg Delay': formatMinutes(data.avg_delay),
                'Cancel Rate': `${data.cancel_rate.toFixed(1)}%`,
                'Total Flights': formatNumber(data.total_flights),
                'Airports': data.airport_count,
                'Carriers': data.carrier_count
              },
              { highlightColor: colorScale(data.delay_rate), showIcon: true, icon: '📍' }
            )
            
            tooltip.show(tooltipHtml, event)
          })
          .on('mousemove', (event) => tooltip.move(event))
          .on('mouseout', function(event, d) {
            const stateCode = fipsToState[d.id]
            const isSelected = props.filters.selectedState === stateCode
            
            d3.select(this)
              .attr('stroke', isSelected ? '#3b82f6' : '#cbd5e1')
              .attr('stroke-width', isSelected ? 3 : 0.8)
            
            tooltip.hide()
          })
          .on('click', (event, d) => {
            const stateCode = fipsToState[d.id]
            emit('state-selected', stateCode)
          })
        
        loading.value = false
      } catch (err) {
        console.error('Error drawing map:', err)
        error.value = 'Failed to load map'
        loading.value = false
      }
    }

    const debouncedDraw = debounce(drawMap, 300)

    onMounted(() => {
      drawMap()
      window.addEventListener('resize', debouncedDraw)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', debouncedDraw)
    })

    watch(() => props.filters, () => {
      drawMap()
    }, { deep: true })

    return {
      chartId,
      loading,
      error,
      legendData,
      resetZoom
    }
  }
}
</script>

<style scoped>
.map-container {
  position: relative;
}

.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  display: flex;
  gap: 8px;
}

.control-btn {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  color: #0f172a;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.control-btn:hover {
  background: #f8fafc;
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.control-btn svg {
  width: 16px;
  height: 16px;
}

.chart-viz {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.state {
  transition: all 0.2s ease;
}

.state:hover {
  opacity: 0.8;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.legend-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0f172a;
  margin-right: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: #475569;
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 3px;
  border: 1px solid #cbd5e1;
}
</style>