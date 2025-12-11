<template>
  <div>
    <div :id="chartId" class="chart-viz"></div>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading airline data...</span>
    </div>
    <!-- Airline Legend -->
    <div class="airline-legend" v-if="!loading && airlines.length > 0">
      <div class="legend-title">Airlines (by On-Time Performance)</div>
      <div class="legend-items">
        <div 
          v-for="(airline, idx) in airlines" 
          :key="airline.carrier"
          class="legend-item"
          :class="{ 
            'selected': filters.selectedCarrier === airline.carrier,
            'dimmed': filters.selectedCarrier && filters.selectedCarrier !== airline.carrier
          }"
          @click="$emit('carrier-selected', airline.carrier)"
          @mouseenter="highlightAirline(airline.carrier)"
          @mouseleave="resetHighlight"
        >
          <div class="legend-color" :style="{ backgroundColor: airline.color }"></div>
          <span class="legend-name">{{ getShortName(airline.carrier) }}</span>
          <span class="legend-ontime">{{ airline.ontime_pct.toFixed(1) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>





<script>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import { createTooltip, formatTooltip, formatNumber, formatDecimal, formatMinutes, airlineColors, debounce } from '@/utils/chartUtils'

export default {
  name: 'ParallelCoordinates',
  props: {
    filters: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['carrier-selected'],
  setup(props, { emit }) {
    const chartId = 'parallel-' + Math.random().toString(36).substr(2, 9)
    const loading = ref(true)
    const airlines = ref([])
    let svg = null
    let brushes = {}
    let hoveredCarrier = null
    let airportMap = null   // airport IATA -> { state }

    // 🔹 Build airport map using IATA code (matches row.airport)
    const buildAirportMap = async () => {
      if (airportMap) return airportMap

      const airports = await d3.csv('/airports_geographic.csv')
      airportMap = {}

      airports.forEach(row => {
        const code = row.iata_code       // <— KEY FIX: use IATA
        if (!code) return

        const stateCode = row.iso_region
          ? row.iso_region.split('-')[1]
          : null

        airportMap[code] = {
          state: stateCode
        }
      })

      return airportMap
    }

    const processData = async () => {
      try {
        const delays = await d3.csv('/Airline_Delay_Cause.csv')
        const airportMapLocal = await buildAirportMap()

        const { selectedState, yearStart, yearEnd } = props.filters || {}

        const carrierMap = {}

        delays.forEach(row => {
          const carrier = row.carrier_name || row.carrier
          if (!carrier) return

          const airport = row.airport
          const airportInfo = airport ? airportMapLocal[airport] : null
          const state = airportInfo?.state || row.airport_state || null

          const year = +row.year || null

          // Year range filter
          if (yearStart != null && yearEnd != null && year) {
            if (year < yearStart || year > yearEnd) return
          }

          // 🔹 STRICT state filter (drop rows without matching state)
          if (selectedState && state !== selectedState) return

          if (!carrierMap[carrier]) {
            carrierMap[carrier] = {
              total_flights: 0,
              total_delay_minutes: 0,
              cancelled: 0,
              delayed: 0,
              ontime: 0,
              weather_delay: 0,
              carrier_delay: 0,
              nas_delay: 0,
              security_delay: 0,
              late_aircraft_delay: 0,
              states: new Set()
            }
          }

          const flights = +row.arr_flights || 0
          const delay = +row.arr_delay || 0
          const cancelled = +row.arr_cancelled || 0
          const delayed = +row.arr_del15 || 0

          carrierMap[carrier].total_flights += flights
          carrierMap[carrier].total_delay_minutes += delay
          carrierMap[carrier].cancelled += cancelled
          carrierMap[carrier].delayed += delayed
          carrierMap[carrier].ontime += Math.max(0, flights - delayed - cancelled)
          carrierMap[carrier].weather_delay += (+row.weather_delay || 0)
          carrierMap[carrier].carrier_delay += (+row.carrier_delay || 0)
          carrierMap[carrier].nas_delay += (+row.nas_delay || 0)
          carrierMap[carrier].security_delay += (+row.security_delay || 0)
          carrierMap[carrier].late_aircraft_delay += (+row.late_aircraft_delay || 0)
          if (state) carrierMap[carrier].states.add(state)
        })

        const data = Object.keys(carrierMap).map(carrier => {
          const stats = carrierMap[carrier]
          const totalDelay = stats.weather_delay + stats.carrier_delay + stats.nas_delay +
                            stats.security_delay + stats.late_aircraft_delay

          return {
            carrier,
            total_flights: stats.total_flights,
            avg_delay_min: stats.total_flights > 0 ? stats.total_delay_minutes / stats.total_flights : 0,
            cancel_rate_pct: stats.total_flights > 0 ? (stats.cancelled / stats.total_flights) * 100 : 0,
            weather_pct: totalDelay > 0 ? (stats.weather_delay / totalDelay) * 100 : 0,
            carrier_pct: totalDelay > 0 ? (stats.carrier_delay / totalDelay) * 100 : 0,
            nas_pct: totalDelay > 0 ? (stats.nas_delay / totalDelay) * 100 : 0,
            late_aircraft_pct: totalDelay > 0 ? (stats.late_aircraft_delay / totalDelay) * 100 : 0,
            ontime_pct: stats.total_flights > 0 ? (stats.ontime / stats.total_flights) * 100 : 0,
            states: Array.from(stats.states)
          }
        })

        return data.sort((a, b) => b.total_flights - a.total_flights).slice(0, 15)
      } catch (err) {
        console.error('Error processing parallel coordinates data:', err)
        throw err
      }
    }

    const getShortName = (carrier) => {
      const shortNames = {
        'American Airlines Inc.': 'American',
        'Delta Air Lines Inc.': 'Delta',
        'United Air Lines Inc.': 'United',
        'Southwest Airlines Co.': 'Southwest',
        'Alaska Airlines Inc.': 'Alaska',
        'JetBlue Airways': 'JetBlue',
        'Spirit Air Lines': 'Spirit',
        'Frontier Airlines Inc.': 'Frontier',
        'Hawaiian Airlines Inc.': 'Hawaiian',
        'Allegiant Air': 'Allegiant'
      }
      return shortNames[carrier] || carrier.replace(' Inc.', '').replace(' Co.', '').slice(0, 15)
    }

    const highlightAirline = (carrier) => {
      hoveredCarrier = carrier
      updateHighlight()
    }

    const resetHighlight = () => {
      hoveredCarrier = null
      updateHighlight()
    }

    const updateHighlight = () => {
      if (!svg) return

      const selectedCarrier = props.filters.selectedCarrier
      const hovered = hoveredCarrier

      svg.selectAll('.pc-line')
        .transition()
        .duration(150)
        .attr('opacity', d => {
          if (hovered) {
            return d.carrier === hovered ? 1 : 0.08
          }
          if (selectedCarrier) {
            return d.carrier === selectedCarrier ? 1 : 0.15
          }
          return 0.5
        })
        .attr('stroke-width', d => {
          if (hovered && d.carrier === hovered) return 4
          if (selectedCarrier && d.carrier === selectedCarrier) return 4
          return 2
        })
    }

    const drawChart = async (animate = true) => {
      try {
        loading.value = true

        const dataRaw = await processData()
        let data = [...dataRaw]

        if (data.length === 0) {
          d3.select(`#${chartId}`).selectAll('*').remove()
          d3.select(`#${chartId}`)
            .append('div')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('justify-content', 'center')
            .style('height', '400px')
            .style('color', 'var(--text-secondary)')
            .text('No airlines match the current filters')
          loading.value = false
          return
        }

        data.sort((a, b) => b.ontime_pct - a.ontime_pct)
        data.forEach((d, i) => {
          d.color = airlineColors[i % airlineColors.length]
        })

        airlines.value = data

        d3.select(`#${chartId}`).selectAll('*').remove()

        const container = document.getElementById(chartId)
        const margin = { top: 50, right: 50, bottom: 30, left: 50 }
        const width = (container?.clientWidth || 1200) - margin.left - margin.right
        const height = 340 - margin.top - margin.bottom

        const svgElement = d3.select(`#${chartId}`)
          .append('svg')
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)

        svg = svgElement.append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`)

        const dimensions = [
          { key: 'total_flights', label: 'Total Flights', format: d => (d / 1000000).toFixed(1) + 'M' },
          { key: 'avg_delay_min', label: 'Avg Delay (min)', format: d => d.toFixed(1) },
          { key: 'cancel_rate_pct', label: 'Cancel Rate %', format: d => d.toFixed(1) + '%' },
          { key: 'weather_pct', label: 'Weather %', format: d => d.toFixed(0) + '%' },
          { key: 'carrier_pct', label: 'Carrier %', format: d => d.toFixed(0) + '%' },
          { key: 'late_aircraft_pct', label: 'Late Aircraft %', format: d => d.toFixed(0) + '%' },
          { key: 'ontime_pct', label: 'On-Time %', format: d => d.toFixed(1) + '%' }
        ]

        const x = d3.scalePoint()
          .domain(dimensions.map(d => d.key))
          .range([0, width])
          .padding(0.1)

        const yScales = {}
        dimensions.forEach(dim => {
          const extent = d3.extent(data, d => d[dim.key])
          const padding = (extent[1] - extent[0]) * 0.1 || 1
          yScales[dim.key] = d3.scaleLinear()
            .domain([extent[0] - padding, extent[1] + padding])
            .range([height, 0])
        })

        const line = d3.line()
          .x(d => x(d.key))
          .y(d => yScales[d.key](d.value))
          .curve(d3.curveMonotoneX)

        const tooltip = createTooltip(chartId)

        svg.append('rect')
          .attr('width', width)
          .attr('height', height)
          .attr('fill', 'transparent')

        const lines = svg.selectAll('.pc-line')
          .data(data)
          .enter()
          .append('path')
          .attr('class', 'pc-line')
          .attr('d', d => {
            const points = dimensions.map(dim => ({
              key: dim.key,
              value: d[dim.key]
            }))
            return line(points)
          })
          .attr('fill', 'none')
          .attr('stroke', d => d.color)
          .attr('stroke-width', 2)
          .attr('opacity', d => {
            if (props.filters.selectedCarrier) {
              return d.carrier === props.filters.selectedCarrier ? 1 : 0.15
            }
            return 0.5
          })
          .style('cursor', 'pointer')
          .on('mouseover', function (event, d) {
            hoveredCarrier = d.carrier
            updateHighlight()

            const html = formatTooltip(
              getShortName(d.carrier),
              {
                'Total Flights': formatNumber(d.total_flights),
                'Avg Delay': formatMinutes(d.avg_delay_min),
                'Cancel Rate': formatDecimal(d.cancel_rate_pct) + '%',
                'On-Time Rate': formatDecimal(d.ontime_pct) + '%',
                'Weather Delays': formatDecimal(d.weather_pct) + '%',
                'Carrier Delays': formatDecimal(d.carrier_pct) + '%'
              },
              { highlightColor: d.color }
            )
            tooltip.show(html, event)
          })
          .on('mousemove', function (event) {
            tooltip.move(event)
          })
          .on('mouseout', function () {
            hoveredCarrier = null
            updateHighlight()
            tooltip.hide()
          })
          .on('click', function (event, d) {
            const isSelected = props.filters.selectedCarrier === d.carrier
            emit('carrier-selected', isSelected ? null : d.carrier)
          })

        if (animate) {
          lines.each(function () {
            const path = d3.select(this)
            const length = this.getTotalLength()
            path
              .attr('stroke-dasharray', length + ' ' + length)
              .attr('stroke-dashoffset', length)
              .transition()
              .duration(1500)
              .ease(d3.easeQuadOut)
              .attr('stroke-dashoffset', 0)
          })
        }

        dimensions.forEach(dim => {
          const axisGroup = svg.append('g')
            .attr('class', 'axis')
            .attr('transform', `translate(${x(dim.key)}, 0)`)

          axisGroup.call(
            d3.axisLeft(yScales[dim.key])
              .ticks(5)
              .tickFormat(dim.format)
          )

axisGroup.selectAll('text')
  .attr('fill', '#ffffff')        // strong contrast for dark background
  .attr('font-size', '0.75rem')
  .style('font-weight', '500')


          axisGroup.selectAll('line, path')
            .attr('stroke', 'var(--border-color)')

axisGroup.append('text')
  .attr('y', -25)
  .attr('text-anchor', 'middle')
  .attr('fill', '#ffffff')        // important: use attr so it wins
  .style('font-weight', '700')
  .style('font-size', '0.8rem')
  .text(dim.label)


          const brush = d3.brushY()
            .extent([[-15, 0], [15, height]])
            .on('brush end', (event) => brushed(event, dim.key))

          axisGroup.append('g')
            .attr('class', 'brush')
            .call(brush)

          brushes[dim.key] = brush
        })

        function brushed(event, key) {
          if (!event.selection) {
            svg.selectAll('.pc-line')
              .attr('opacity', d => {
                if (props.filters.selectedCarrier) {
                  return d.carrier === props.filters.selectedCarrier ? 1 : 0.15
                }
                return 0.5
              })
            return
          }

          const [y0, y1] = event.selection
          const scale = yScales[key]
          const [min, max] = [scale.invert(y1), scale.invert(y0)]

          svg.selectAll('.pc-line')
            .attr('opacity', d => {
              const value = d[key]
              const inBrush = value >= min && value <= max
              if (!inBrush) return 0.05
              if (props.filters.selectedCarrier) {
                return d.carrier === props.filters.selectedCarrier ? 1 : 0.3
              }
              return 0.7
            })
        }

        loading.value = false
      } catch (err) {
        console.error('Error drawing parallel coordinates:', err)
        loading.value = false
      }
    }

    // Carrier selection highlight
    watch(
      () => props.filters.selectedCarrier,
      () => {
        updateHighlight()
      }
    )

    // 🔹 Redraw when state or year range changes
    watch(
      () => [props.filters.selectedState, props.filters.yearStart, props.filters.yearEnd],
      () => {
        drawChart(false)
      }
    )

    const handleResize = debounce(() => drawChart(false), 250)

    onMounted(() => {
      drawChart(true)
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    return {
      chartId,
      loading,
      airlines,
      getShortName,
      highlightAirline,
      resetHighlight
    }
  }
}
</script>
<style scoped>
/* Chart Container */
/* Chart Container */
.chart-viz {
  width: 100%;
  min-height: 340px;
  position: relative;
}

/* Loading Spinner */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 340px;
  gap: 15px;
}

/* Airline Legend */
.airline-legend {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid var(--border-color);
  color: #ffffff; 
}

/* Legend Title */
.legend-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary); /* Adjusted for better contrast */
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

/* Legend Items Layout */
.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: #ffffff; 
}

/* Individual Legend Item */
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);  /* Slightly brighter */
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  color: #ffffff; 
}

/* Hover Effect on Legend Item */
.legend-item:hover {
  background: rgba(255, 255, 255, 0.15); /* More pronounced hover effect */
  border-color: rgba(255, 255, 255, 0.2); /* Lighter border color on hover */
}

/* Selected Legend Item */
.legend-item.selected {
  background: rgba(102, 126, 234, 0.2); /* Lighter selection color */
  border-color: var(--primary); /* Keep primary border color for selection */
  color: #ffffff; 
}

/* Dimmed Legend Item */
.legend-item.dimmed {
  opacity: 0.5; /* Reduced opacity for dimmed items */
}

/* Legend Color Box */
.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

/* Legend Name */
.legend-name {
  font-size: 0.8rem;
  color: #ffffff;  /* Primary text color */
  font-weight: 600;  /* Increased font weight for emphasis */
}

/* Legend On-Time Percentage */
.legend-ontime {
  font-size: 0.75rem;
  color: var(--primary); /* Brighter color for on-time percentage */
  font-weight: 600;
  margin-left: auto;
  color: #ffffff; 
}

/* Parallel Coordinates Line Styling */
:deep(.pc-line) {
  transition: opacity 0.15s ease, stroke-width 0.15s ease;
}

/* Brush Selection (for filtering) */
:deep(.brush .selection) {
  fill: var(--primary);
  fill-opacity: 0.2;
  stroke: var(--primary);
  stroke-width: 1;
}

/* Axis Labels in Parallel Coordinates */
/* Axis labels in Parallel Coordinates (SVG text) */
:deep(.axis text) {
  fill: #e5e7eb;     /* or #ffffff if background is dark */
  font-weight: 600;
  font-size: 0.75rem;
}



/* Axis Grid Lines in Parallel Coordinates */
.chart-viz .axis line, 
.chart-viz .axis path {
  stroke: var(--border-color);  /* Lighten up the grid lines */
}

/* Tooltip Text Color */
.d3-tooltip {
  color: #ffffff;  /* Consistent with the UI text color */
}

/* Tooltip Styling */
.d3-tooltip {
  font-family: 'Inter', sans-serif;
  position: absolute;
  background: rgba(15, 23, 42, 0.96);
  color: white;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.85rem;
  pointer-events: none;
  opacity: 0;
  z-index: 1000;
  max-width: 300px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: opacity 0.15s ease;
}

/* Tooltip Styling when Visible */
.d3-tooltip.show {
  opacity: 1;
  transition: opacity 0.15s ease;
}
</style>