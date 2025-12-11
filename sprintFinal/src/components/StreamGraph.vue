<template>
  <div>
    <div :id="chartId" class="chart-viz"></div>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading temporal data...</span>
    </div>
    <div class="legend" v-if="!loading">
      <div 
        v-for="(item, idx) in legendData" 
        :key="idx" 
        class="legend-item"
        :class="{ 
          'selected': filters.selectedDelayType === item.key,
          'dimmed': filters.selectedDelayType && filters.selectedDelayType !== item.key
        }"
        @click="$emit('delay-type-selected', item.key)"
      >
        <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
        <span>{{ item.label }}</span>
      </div>
    </div>
  </div>
</template>





<script>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import { createTooltip, formatTooltip, formatNumber, delayColors, abbreviateNumber, debounce } from '@/utils/chartUtils'

export default {
  name: 'StreamGraph',
  props: {
    filters: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['delay-type-selected'],
  setup(props, { emit }) {
    const chartId = 'stream-' + Math.random().toString(36).substr(2, 9)
    const loading = ref(true)
    const legendData = ref([])
    let svg = null
    let airportMap = null   // airport IATA -> { state, lat, lon }

    const buildAirportMap = async () => {
      if (airportMap) return airportMap

      const airports = await d3.csv('/airports_geographic.csv')
      airportMap = {}

      airports.forEach(row => {
        const code = row.iata_code          // 🔹 use IATA
        if (!code) return

        const stateCode = row.iso_region
          ? row.iso_region.split('-')[1]
          : null

        airportMap[code] = {
          state: stateCode,
          lat: +row.latitude_deg,
          lon: +row.longitude_deg
        }
      })

      return airportMap
    }

    // Re-aggregate every time so filters are always honored
    const processData = async () => {
      try {
        const delays = await d3.csv('/Airline_Delay_Cause.csv')
        const airportMapLocal = await buildAirportMap()

        const { selectedState, yearStart, yearEnd } = props.filters || {}

        const timeMap = {}

        delays.forEach(row => {
          const year = +row.year
          const month = +row.month
          if (!year || !month) return

          const airport = row.airport
          const airportInfo = airport ? airportMapLocal[airport] : null
          const state = airportInfo?.state || row.airport_state || null
          const carrier = row.carrier_name || row.carrier

          // Year range filter
          if (yearStart != null && yearEnd != null) {
            if (year < yearStart || year > yearEnd) return
          }

          // 🔹 STRICT state filter
          if (selectedState && state !== selectedState) return

          const yearMonth = `${year}-${month.toString().padStart(2, '0')}`

          if (!timeMap[yearMonth]) {
            timeMap[yearMonth] = {
              carrier_delay: 0,
              weather_delay: 0,
              nas_delay: 0,
              security_delay: 0,
              late_aircraft_delay: 0,
              states: new Set(),
              carriers: new Set()
            }
          }

          timeMap[yearMonth].carrier_delay += (+row.carrier_delay || 0)
          timeMap[yearMonth].weather_delay += (+row.weather_delay || 0)
          timeMap[yearMonth].nas_delay += (+row.nas_delay || 0)
          timeMap[yearMonth].security_delay += (+row.security_delay || 0)
          timeMap[yearMonth].late_aircraft_delay += (+row.late_aircraft_delay || 0)

          if (state) timeMap[yearMonth].states.add(state)
          if (carrier) timeMap[yearMonth].carriers.add(carrier)
        })

        return Object.keys(timeMap)
          .sort()
          .map(date => ({
            date,
            carrier_delay: timeMap[date].carrier_delay,
            weather_delay: timeMap[date].weather_delay,
            nas_delay: timeMap[date].nas_delay,
            security_delay: timeMap[date].security_delay,
            late_aircraft_delay: timeMap[date].late_aircraft_delay,
            states: Array.from(timeMap[date].states),
            carriers: Array.from(timeMap[date].carriers)
          }))
      } catch (err) {
        console.error('Error processing stream data:', err)
        throw err
      }
    }

    const drawChart = async (animate = true) => {
      try {
        loading.value = true

        const data = await processData()

        d3.select(`#${chartId}`).selectAll('*').remove()

        const container = document.getElementById(chartId)
        if (!container || data.length === 0) {
          loading.value = false
          return
        }

        const margin = { top: 20, right: 30, bottom: 50, left: 70 }
        const width = (container?.clientWidth || 900) - margin.left - margin.right
        const height = 280 - margin.top - margin.bottom

        const svgElement = d3.select(`#${chartId}`)
          .append('svg')
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)

        svg = svgElement.append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`)

        const keys = ['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
        const stack = d3.stack().keys(keys).offset(d3.stackOffsetWiggle)
        const series = stack(data)

        const xScale = d3.scalePoint()
          .domain(data.map(d => d.date))
          .range([0, width])

        const yExtent = d3.extent(series.flat(2))
        const yScale = d3.scaleLinear()
          .domain(yExtent)
          .range([height, 0])

        const area = d3.area()
          .x(d => xScale(d.data.date))
          .y0(d => yScale(d[0]))
          .y1(d => yScale(d[1]))
          .curve(d3.curveCatmullRom)

        const colorMap = {
          carrier_delay: delayColors.carrier,
          weather_delay: delayColors.weather,
          nas_delay: delayColors.nas,
          security_delay: delayColors.security,
          late_aircraft_delay: delayColors.late_aircraft
        }

        const labelMap = {
          carrier_delay: 'Carrier',
          weather_delay: 'Weather',
          nas_delay: 'NAS',
          security_delay: 'Security',
          late_aircraft_delay: 'Late Aircraft'
        }

        const tooltip = createTooltip(chartId)

        const layers = svg.selectAll('.layer')
          .data(series)
          .enter()
          .append('path')
          .attr('class', 'layer')
          .attr('d', area)
          .attr('fill', d => colorMap[d.key])
          .attr('opacity', d => {
            if (props.filters.selectedDelayType) {
              return d.key === props.filters.selectedDelayType ? 1 : 0.2
            }
            return 0.85
          })
          .style('cursor', 'pointer')
          .on('mouseover', function (event, d) {
            d3.select(this).attr('opacity', 1)

            svg.selectAll('.layer')
              .filter(node => node !== d)
              .attr('opacity', 0.2)

            const layerName = labelMap[d.key]
            const total = d3.sum(d, point => point[1] - point[0])
            const avgPerMonth = total / d.length

            const html = formatTooltip(
              `${layerName} Delays`,
              {
                'Total Delay': abbreviateNumber(Math.round(total)) + ' min',
                'Avg per Month': abbreviateNumber(Math.round(avgPerMonth)) + ' min',
                'Data Points': d.length + ' months'
              },
              { highlightColor: colorMap[d.key] }
            )
            tooltip.show(html, event)
          })
          .on('mousemove', function (event) {
            tooltip.move(event)
          })
          .on('mouseout', function () {
            svg.selectAll('.layer')
              .attr('opacity', d => {
                if (props.filters.selectedDelayType) {
                  return d.key === props.filters.selectedDelayType ? 1 : 0.2
                }
                return 0.85
              })
            tooltip.hide()
          })
          .on('click', function (event, d) {
            const isSelected = props.filters.selectedDelayType === d.key
            emit('delay-type-selected', isSelected ? null : d.key)
          })

        if (animate) {
          layers
            .attr('opacity', 0)
            .transition()
            .duration(800)
            .delay((d, i) => i * 100)
            .attr('opacity', d => {
              if (props.filters.selectedDelayType) {
                return d.key === props.filters.selectedDelayType ? 1 : 0.2
              }
              return 0.85
            })
        }

        const xAxis = svg.append('g')
          .attr('transform', `translate(0,${height})`)
          .call(
            d3.axisBottom(xScale)
              .tickValues(data.filter((d, i) => i % 12 === 0).map(d => d.date))
              .tickFormat(d => d.split('-')[0])
          )

        xAxis.selectAll('text')
          .attr('fill', 'var(--text-secondary)')
        xAxis.selectAll('line, path')
          .attr('stroke', 'var(--border-color)')

        const yAxis = svg.append('g')
          .call(
            d3.axisLeft(yScale)
              .ticks(6)
              .tickFormat(d => abbreviateNumber(Math.abs(d)))
          )

        yAxis.selectAll('text')
          .attr('fill', 'var(--text-secondary)')
        yAxis.selectAll('line, path')
          .attr('stroke', 'var(--border-color)')

        svg.append('text')
          .attr('transform', 'rotate(-90)')
          .attr('y', -55)
          .attr('x', -height / 2)
          .attr('text-anchor', 'middle')
          .style('font-size', '0.8rem')
          .style('fill', 'var(--text-secondary)')
          .text('Delay Minutes')

        const hoverLine = svg.append('line')
          .attr('class', 'hover-line')
          .attr('y1', 0)
          .attr('y2', height)
          .attr('stroke', 'rgba(255,255,255,0.3)')
          .attr('stroke-dasharray', '4,4')
          .style('opacity', 0)
          .style('pointer-events', 'none')

        svg.append('rect')
          .attr('width', width)
          .attr('height', height)
          .attr('fill', 'transparent')
          .on('mousemove', function (event) {
            const [mx] = d3.pointer(event)
            hoverLine
              .attr('x1', mx)
              .attr('x2', mx)
              .style('opacity', 1)
          })
          .on('mouseout', function () {
            hoverLine.style('opacity', 0)
          })

        legendData.value = [
          { key: 'carrier_delay', label: 'Carrier', color: delayColors.carrier },
          { key: 'weather_delay', label: 'Weather', color: delayColors.weather },
          { key: 'nas_delay', label: 'NAS', color: delayColors.nas },
          { key: 'security_delay', label: 'Security', color: delayColors.security },
          { key: 'late_aircraft_delay', label: 'Late Aircraft', color: delayColors.late_aircraft }
        ]

        loading.value = false
      } catch (err) {
        console.error('Error drawing stream graph:', err)
        loading.value = false
      }
    }

    const updateSelection = () => {
      if (!svg) return

      svg.selectAll('.layer')
        .transition()
        .duration(300)
        .attr('opacity', d => {
          if (props.filters.selectedDelayType) {
            return d.key === props.filters.selectedDelayType ? 1 : 0.2
          }
          return 0.85
        })
    }

    watch(() => props.filters.selectedDelayType, updateSelection)

    // 🔹 Redraw when state changes
    watch(
      () => props.filters.selectedState,
      () => {
        drawChart(false)
      }
    )

    // 🔹 Redraw when year range changes
    watch(
      () => [props.filters.yearStart, props.filters.yearEnd],
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

    return { chartId, loading, legendData }
  }
}
</script>







<style scoped>
.chart-viz {
  width: 100%;
  min-height: 280px;
  position: relative;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 280px;
  gap: 15px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 15px;
  font-size: 0.85rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.03);
}

.legend-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.legend-item.selected {
  background: rgba(102, 126, 234, 0.15);
  outline: 1px solid var(--primary);
}

.legend-item.dimmed {
  opacity: 0.4;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

:deep(.layer) {
  transition: opacity 0.3s ease;
}
</style>
