<template>
  <div>
    <div :id="chartId" class="chart-viz"></div>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading map data...</span>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div class="legend" v-if="!loading && !error">
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
  formatPercentRaw,
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
    let svg, tooltip, stateData, colorScale

    const processData = async () => {
      try {
        const delays = await d3.csv('/Airline_Delay_Cause.csv')
        const airports = await d3.csv('/airports_geographic.csv')
        
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
          const carrier = row.carrier_name || row.carrier
          
          if (!state) return
          
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
        const height = Math.max(200, width * 0.45)
        
        const svgElement = d3.select(`#${chartId}`)
          .append('svg')
          .attr('width', width)
          .attr('height', height)
        
        svg = svgElement
        
        const projection = d3.geoAlbersUsa()
          .translate([width / 2, height / 2])
          .scale(width * 1.1)
        
        const path = d3.geoPath().projection(projection)
        
        // Color scale
        const delayValues = Object.values(stateData).map(d => d.avg_delay)
        colorScale = d3.scaleSequential()
          .domain([d3.min(delayValues), d3.max(delayValues)])
          .interpolator(d3.interpolateYlOrRd)
        
        // Create legend
        const min = d3.min(delayValues)
        const max = d3.max(delayValues)
        const mid = (min + max) / 2
        legendData.value = [
          { label: `Low (${formatDecimal(min)} min)`, color: colorScale(min) },
          { label: `Medium (${formatDecimal(mid)} min)`, color: colorScale(mid) },
          { label: `High (${formatDecimal(max)} min)`, color: colorScale(max) }
        ]
        
        tooltip = createTooltip(chartId)
        
        const statesGeo = topojson.feature(us, us.objects.states)
        
        const g = svgElement.append('g')
        
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
            return data ? colorScale(data.avg_delay) : '#3a3a3a'
          })
          .attr('stroke', d => {
            const stateCode = fipsToState[d.id]
            if (props.filters.selectedState === stateCode) {
              return '#667eea'
            }
            return 'rgba(255,255,255,0.3)'
          })
          .attr('stroke-width', d => {
            const stateCode = fipsToState[d.id]
            return props.filters.selectedState === stateCode ? 3 : 1
          })
          .attr('opacity', d => {
            const stateCode = fipsToState[d.id]
            if (props.filters.selectedState && props.filters.selectedState !== stateCode) {
              return 0.4
            }
            return 1
          })
          .style('cursor', 'pointer')
          .on('mouseover', function(event, d) {
            const stateCode = fipsToState[d.id]
            const data = stateData[stateCode]
            
            if (data) {
              d3.select(this)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2)
              
              const stateName = stateNames[stateCode] || stateCode
              
              const html = formatTooltip(
                `${stateName} (${stateCode})`,
                {
                  'Total Flights': formatNumber(data.total_flights),
                  'Avg Delay': formatMinutes(data.avg_delay),
                  'Delay Rate': formatPercentRaw(data.delay_rate) + '%',
                  'Cancel Rate': formatPercentRaw(data.cancel_rate) + '%',
                  'Airports': data.airport_count,
                  'Airlines': data.carrier_count
                },
                { highlightColor: colorScale(data.avg_delay) }
              )
              
              tooltip.show(html, event)
            }
          })
          .on('mousemove', function(event) {
            tooltip.move(event)
          })
          .on('mouseout', function(event, d) {
            const stateCode = fipsToState[d.id]
            d3.select(this)
              .attr('stroke', props.filters.selectedState === stateCode ? '#667eea' : 'rgba(255,255,255,0.3)')
              .attr('stroke-width', props.filters.selectedState === stateCode ? 3 : 1)
            tooltip.hide()
          })
          .on('click', function(event, d) {
            const stateCode = fipsToState[d.id]
            const data = stateData[stateCode]
            
            if (data) {
              const isCurrentlySelected = props.filters.selectedState === stateCode
              emit('state-selected', isCurrentlySelected ? null : stateCode)
            }
          })
        
        // Fade in animation
        g.selectAll('.state')
          .style('opacity', 0)
          .transition()
          .duration(600)
          .style('opacity', d => {
            const stateCode = fipsToState[d.id]
            if (props.filters.selectedState && props.filters.selectedState !== stateCode) {
              return 0.4
            }
            return 1
          })
        
        loading.value = false
      } catch (err) {
        console.error('Error drawing map:', err)
        error.value = 'Failed to load map data'
        loading.value = false
      }
    }

    const updateSelection = () => {
      if (!svg) return
      
      svg.selectAll('.state')
        .transition()
        .duration(300)
        .attr('stroke', d => {
          const stateCode = fipsToState[d.id]
          if (props.filters.selectedState === stateCode) {
            return '#667eea'
          }
          return 'rgba(255,255,255,0.3)'
        })
        .attr('stroke-width', d => {
          const stateCode = fipsToState[d.id]
          return props.filters.selectedState === stateCode ? 3 : 1
        })
        .attr('opacity', d => {
          const stateCode = fipsToState[d.id]
          if (props.filters.selectedState && props.filters.selectedState !== stateCode) {
            return 0.4
          }
          return 1
        })
    }

    watch(() => props.filters.selectedState, updateSelection)

    const handleResize = debounce(drawMap, 250)

    onMounted(() => {
      drawMap()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    return {
      chartId,
      loading,
      error,
      legendData
    }
  }
}
</script>

<style scoped>
.chart-viz {
  width: 100%;
  min-height: 220px;
  position: relative;
}

.loading,
.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 220px;
  font-size: 1.1rem;
  color: var(--text-secondary);
  gap: 15px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 15px;
  font-size: 0.85rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

:deep(.state) {
  transition: opacity 0.3s ease, stroke 0.2s ease, stroke-width 0.2s ease;
}
</style>
