<template>
  <div>
    <div :id="chartId" class="chart-viz"></div>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading hierarchy...</span>
    </div>
    <!-- Breadcrumb Navigation -->
    <div class="breadcrumb" v-if="!loading && breadcrumb.length > 0">
      <span 
        v-for="(crumb, idx) in breadcrumb" 
        :key="idx"
        class="crumb"
        @click="navigateTo(crumb)"
      >
        {{ crumb.name }}
        <span v-if="idx < breadcrumb.length - 1" class="separator">→</span>
      </span>
    </div>
    <!-- Legend -->
    <div class="sunburst-legend" v-if="!loading">
      <div class="legend-section">
        <span class="legend-title">Hierarchy Levels</span>
        <div class="legend-items">
          <div class="legend-item">
            <div class="legend-color" style="background: #48bb78;"></div>
            <span>State</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: #ed8936;"></div>
            <span>Airport</span>
          </div>
        </div>
      </div>
      <div class="legend-section">
        <span class="legend-title">Delay Types</span>
        <div class="legend-items">
          <div v-for="(color, type) in delayTypeColors" :key="type" class="legend-item">
            <div class="legend-color" :style="{ backgroundColor: color }"></div>
            <span>{{ type }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import { createTooltip, formatTooltip, formatMinutes, formatPercentRaw, delayColors, abbreviateNumber, debounce } from '@/utils/chartUtils'

export default {
  name: 'SunburstChart',
  props: {
    filters: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['delay-type-selected'],
  setup(props, { emit }) {
    const chartId = 'sunburst-' + Math.random().toString(36).substr(2, 9)
    const loading = ref(true)
    const breadcrumb = ref([])
    let svg, tooltip, fullData, currentRoot
    
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
              state: row.iso_region ? row.iso_region.split('-')[1] : null
            }
          }
        })
        
        // Build hierarchy: Root -> States -> Airports -> Delay Types
        const hierarchy = {
          name: 'US Airports',
          children: []
        }
        
        const stateMap = {}
        
        delays.forEach(row => {
          const airport = row.airport
          const airportInfo = airportMap[airport]
          const state = airportInfo?.state || row.airport_state
          
          if (!state) return
          
          // Apply state filter
          if (props.filters.selectedState && state !== props.filters.selectedState) {
            return
          }
          
          if (!stateMap[state]) {
            stateMap[state] = {
              name: state,
              children: [],
              airportMap: {}
            }
          }
          
          if (!stateMap[state].airportMap[airport]) {
            stateMap[state].airportMap[airport] = {
              name: airport,
              fullName: airportInfo?.name || airport,
              children: [],
              delayMap: {}
            }
          }
          
          // Add delay types
          const delayTypes = [
            { name: 'Carrier', value: +row.carrier_delay || 0, key: 'carrier_delay' },
            { name: 'Weather', value: +row.weather_delay || 0, key: 'weather_delay' },
            { name: 'NAS', value: +row.nas_delay || 0, key: 'nas_delay' },
            { name: 'Security', value: +row.security_delay || 0, key: 'security_delay' },
            { name: 'Late Aircraft', value: +row.late_aircraft_delay || 0, key: 'late_aircraft_delay' }
          ]
          
          const airportNode = stateMap[state].airportMap[airport]
          
          delayTypes.forEach(type => {
            if (type.value > 0) {
              if (!airportNode.delayMap[type.name]) {
                airportNode.delayMap[type.name] = {
                  name: type.name,
                  key: type.key,
                  value: 0
                }
              }
              airportNode.delayMap[type.name].value += type.value
            }
          })
        })
        
        // Convert maps to arrays
        Object.values(stateMap).forEach(state => {
          state.children = Object.values(state.airportMap).map(airport => {
            airport.children = Object.values(airport.delayMap)
            delete airport.delayMap
            return airport
          })
          // Sort airports by total delay and limit to top 10 per state
          state.children.sort((a, b) => {
            const aTotal = a.children.reduce((sum, c) => sum + c.value, 0)
            const bTotal = b.children.reduce((sum, c) => sum + c.value, 0)
            return bTotal - aTotal
          })
          state.children = state.children.slice(0, 10)
          delete state.airportMap
        })
        
        hierarchy.children = Object.values(stateMap)
          .sort((a, b) => {
            const aTotal = a.children.reduce((sum, airport) => 
              sum + airport.children.reduce((s, d) => s + d.value, 0), 0)
            const bTotal = b.children.reduce((sum, airport) => 
              sum + airport.children.reduce((s, d) => s + d.value, 0), 0)
            return bTotal - aTotal
          })
          .slice(0, 15) // Top 15 states
        
        return hierarchy
      } catch (err) {
        console.error('Error processing sunburst data:', err)
        throw err
      }
    }

    const navigateTo = (crumb) => {
      // Reset breadcrumb to the clicked position
      const idx = breadcrumb.value.indexOf(crumb)
      breadcrumb.value = breadcrumb.value.slice(0, idx + 1)
      // Could implement zoom here
    }

    const drawSunburst = async (animate = true) => {
      try {
        loading.value = true
        
        fullData = await processData()
        
        if (!fullData.children || fullData.children.length === 0) {
          d3.select(`#${chartId}`).selectAll('*').remove()
          d3.select(`#${chartId}`)
            .append('div')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('justify-content', 'center')
            .style('height', '450px')
            .style('color', 'var(--text-secondary)')
            .text('No data available for current filters')
          loading.value = false
          return
        }
        
        d3.select(`#${chartId}`).selectAll('*').remove()
        
        const container = document.getElementById(chartId)
        const width = Math.min(container?.clientWidth || 550, 550)
        const height = width
        const radius = Math.min(width, height) / 2
        
        const svgElement = d3.select(`#${chartId}`)
          .append('svg')
          .attr('width', width)
          .attr('height', height)
        
        svg = svgElement.append('g')
          .attr('transform', `translate(${width/2},${height/2})`)
        
        const partition = d3.partition().size([2 * Math.PI, radius])
        const root = d3.hierarchy(fullData)
          .sum(d => d.value || 0)
          .sort((a, b) => b.value - a.value)
        
        partition(root)
        currentRoot = root
        
        // Initialize breadcrumb
        breadcrumb.value = [{ name: 'All States', node: root }]
        
        const arc = d3.arc()
          .startAngle(d => d.x0)
          .endAngle(d => d.x1)
          .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
          .padRadius(radius / 2)
          .innerRadius(d => d.y0)
          .outerRadius(d => d.y1 - 1)
        
        tooltip = createTooltip(chartId)
        
        const getColor = (d) => {
          if (d.depth === 3) {
            // Delay type level
            return delayColors[d.data.name] || '#667eea'
          } else if (d.depth === 2) {
            // Airport level
            return '#ed8936'
          } else if (d.depth === 1) {
            // State level
            return '#48bb78'
          }
          return '#667eea'
        }
        
        const getOpacity = (d) => {
          if (props.filters.selectedDelayType && d.depth === 3) {
            return d.data.key === props.filters.selectedDelayType ? 1 : 0.3
          }
          return 0.85
        }
        
        const paths = svg.selectAll('.arc')
          .data(root.descendants().filter(d => d.depth > 0))
          .enter()
          .append('path')
          .attr('class', 'arc')
          .attr('d', arc)
          .attr('fill', getColor)
          .attr('opacity', 0)
          .attr('stroke', 'var(--bg-card)')
          .attr('stroke-width', 0.5)
          .style('cursor', 'pointer')
          .on('mouseover', function(event, d) {
            d3.select(this)
              .attr('opacity', 1)
              .attr('stroke', '#fff')
              .attr('stroke-width', 2)
            
            // Build path string
            const pathParts = []
            let current = d
            while (current) {
              if (current.data.name !== 'US Airports') {
                pathParts.unshift(current.data.name)
              }
              current = current.parent
            }
            
            const percentage = ((d.value / root.value) * 100)
            
            const tooltipData = {
              'Total Delay': abbreviateNumber(Math.round(d.value)) + ' min',
              'Percentage': formatPercentRaw(percentage) + '%'
            }
            
            if (d.depth === 2 && d.data.fullName) {
              tooltipData['Full Name'] = d.data.fullName
            }
            
            if (d.children) {
              tooltipData['Sub-items'] = d.children.length
            }
            
            const html = formatTooltip(
              pathParts.join(' → '),
              tooltipData,
              { highlightColor: getColor(d) }
            )
            tooltip.show(html, event)
          })
          .on('mousemove', function(event) {
            tooltip.move(event)
          })
          .on('mouseout', function(event, d) {
            d3.select(this)
              .attr('opacity', getOpacity(d))
              .attr('stroke', 'var(--bg-card)')
              .attr('stroke-width', 0.5)
            tooltip.hide()
          })
          .on('click', function(event, d) {
            // Emit delay type selection for depth 3
            if (d.depth === 3 && d.data.key) {
              const isSelected = props.filters.selectedDelayType === d.data.key
              emit('delay-type-selected', isSelected ? null : d.data.key)
            }
            
            // Update breadcrumb
            const pathParts = []
            let current = d
            while (current) {
              pathParts.unshift({ name: current.data.name, node: current })
              current = current.parent
            }
            breadcrumb.value = pathParts.filter(p => p.name !== 'US Airports')
            if (breadcrumb.value.length === 0) {
              breadcrumb.value = [{ name: 'All States', node: root }]
            }
          })
        
        // Animate appearance
        if (animate) {
          paths.transition()
            .duration(800)
            .delay((d, i) => i * 3)
            .attr('opacity', getOpacity)
        } else {
          paths.attr('opacity', getOpacity)
        }
        
        // Add center text
        svg.append('text')
          .attr('text-anchor', 'middle')
          .attr('dy', '-0.5em')
          .style('fill', 'var(--text-primary)')
          .style('font-size', '1.1rem')
          .style('font-weight', '600')
          .text('Delay')
        
        svg.append('text')
          .attr('text-anchor', 'middle')
          .attr('dy', '0.8em')
          .style('fill', 'var(--text-primary)')
          .style('font-size', '1.1rem')
          .style('font-weight', '600')
          .text('Hierarchy')
        
        svg.append('text')
          .attr('text-anchor', 'middle')
          .attr('dy', '2.5em')
          .style('fill', 'var(--text-muted)')
          .style('font-size', '0.75rem')
          .text(abbreviateNumber(Math.round(root.value)) + ' min total')
        
        loading.value = false
      } catch (err) {
        console.error('Error drawing sunburst:', err)
        loading.value = false
      }
    }

    const updateSelection = () => {
      if (!svg) return
      
      svg.selectAll('.arc')
        .transition()
        .duration(300)
        .attr('opacity', d => {
          if (props.filters.selectedDelayType && d.depth === 3) {
            return d.data.key === props.filters.selectedDelayType ? 1 : 0.3
          }
          return 0.85
        })
    }

    watch(() => props.filters.selectedDelayType, updateSelection)
    watch(() => props.filters.selectedState, () => drawSunburst(false))

    const handleResize = debounce(() => drawSunburst(false), 250)

    onMounted(() => {
      drawSunburst(true)
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    return { chartId, loading, breadcrumb, delayTypeColors, navigateTo }
  }
}
</script>

<style scoped>
.chart-viz {
  width: 100%;
  min-height: 450px;
  position: relative;
  display: flex;
  justify-content: center;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 450px;
  gap: 15px;
}

.breadcrumb {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 15px;
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  font-size: 0.85rem;
}

.crumb {
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s;
}

.crumb:hover {
  color: var(--primary);
}

.crumb:last-child {
  color: var(--text-primary);
  font-weight: 600;
}

.separator {
  color: var(--text-muted);
  margin: 0 5px;
}

.sunburst-legend {
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
  gap: 8px;
}

.legend-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

:deep(.arc) {
  transition: opacity 0.3s ease, stroke 0.2s ease;
}
</style>
