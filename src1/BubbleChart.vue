<template>
    <div>
      <div :id="chartId" class="chart-viz"></div>
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <span>Loading airport data...</span>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, watch } from 'vue'
  import * as d3 from 'd3'
  import { createTooltip, formatTooltip, formatNumber, formatMinutes, delayColors } from '@/utils/chartUtils'
  
  export default {
    name: 'BubbleChart',
    props: {
      selectedState: String,
      selectedAirport: String
    },
    emits: ['airport-selected'],
    setup(props, { emit }) {
      const chartId = 'bubble-' + Math.random().toString(36).substr(2, 9)
      const loading = ref(true)
  
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
          
          // Aggregate by airport
          const airportData = {}
          
          delays.forEach(row => {
            const airport = row.airport
            if (!airport) return
            
            const airportInfo = airportMap[airport]
            const state = airportInfo?.state || row.airport_state
            
            if (!airportData[airport]) {
              airportData[airport] = {
                airport_code: airport,
                airport_name: airportInfo?.name || airport,
                state: state,
                total_flights: 0,
                total_delay: 0,
                total_cancelled: 0,
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
            
            airportData[airport].total_flights += flights
            airportData[airport].total_delay += delay
            airportData[airport].total_cancelled += cancelled
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
            
            return {
              ...d,
              avg_delay_min: d.total_flights > 0 ? d.total_delay / d.total_flights : 0,
              dominant_delay_type: maxDelayType
            }
          })
          
          // Filter by state if selected
          if (props.selectedState) {
            data = data.filter(d => d.state === props.selectedState)
          }
          
          // Sort by flights and take top 50
          return data.sort((a, b) => b.total_flights - a.total_flights).slice(0, 50)
        } catch (err) {
          console.error('Error processing bubble chart data:', err)
          throw err
        }
      }
  
      const drawChart = async () => {
        try {
          loading.value = true
          
          const data = await processData()
          
          d3.select(`#${chartId}`).selectAll('*').remove()
          
          const container = document.getElementById(chartId)
          const margin = { top: 20, right: 80, bottom: 60, left: 80 }
          const width = (container?.clientWidth || 600) - margin.left - margin.right
          const height = 450 - margin.top - margin.bottom
          
          const svg = d3.select(`#${chartId}`)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`)
          
          const xScale = d3.scaleLog()
            .domain(d3.extent(data, d => d.total_flights))
            .range([0, width])
            .nice()
          
          const yScale = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.avg_delay_min)])
            .range([height, 0])
            .nice()
          
          const radiusScale = d3.scaleSqrt()
            .domain([0, d3.max(data, d => d.total_cancelled)])
            .range([3, 30])
          
          const colorScale = d3.scaleOrdinal()
            .domain(['carrier', 'weather', 'nas', 'security', 'late_aircraft', 'unknown'])
            .range([
              delayColors.carrier,
              delayColors.weather,
              delayColors.nas,
              delayColors.security,
              delayColors.late_aircraft,
              '#95a5a6'
            ])
          
          const tooltip = createTooltip(chartId)
          
          const bubbles = svg.selectAll('.bubble')
            .data(data)
            .enter()
            .append('circle')
            .attr('class', 'bubble')
            .attr('cx', d => xScale(d.total_flights))
            .attr('cy', d => yScale(d.avg_delay_min))
            .attr('r', 0)
            .attr('fill', d => colorScale(d.dominant_delay_type))
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .attr('opacity', 0.7)
            .style('cursor', 'pointer')
            .on('mouseover', function(event, d) {
              d3.select(this).attr('opacity', 1).attr('stroke', '#333').attr('stroke-width', 2)
              
              const html = formatTooltip(
                `${d.airport_code} - ${d.airport_name}`,
                {
                  'State': d.state,
                  'Total Flights': formatNumber(d.total_flights),
                  'Avg Delay': formatMinutes(d.avg_delay_min),
                  'Cancellations': formatNumber(d.total_cancelled),
                  'Main Delay': d.dominant_delay_type.toUpperCase()
                }
              )
              tooltip.show(html, event)
            })
            .on('mouseout', function() {
              if (!d3.select(this).classed('selected')) {
                d3.select(this).attr('opacity', 0.7).attr('stroke', '#fff').attr('stroke-width', 1.5)
              }
              tooltip.hide()
            })
            .on('click', function(event, d) {
              const isSelected = d3.select(this).classed('selected')
              d3.selectAll('.bubble').classed('selected', false)
              
              if (!isSelected) {
                d3.select(this).classed('selected', true)
                emit('airport-selected', d.airport_code)
              } else {
                emit('airport-selected', null)
              }
            })
          
          // Animate bubble appearance
          bubbles.transition()
            .duration(800)
            .delay((d, i) => i * 20)
            .attr('r', d => radiusScale(d.total_cancelled))
          
          // X Axis
          svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale).ticks(5, '.0s'))
          
          svg.append('text')
            .attr('x', width / 2)
            .attr('y', height + 45)
            .attr('text-anchor', 'middle')
            .style('font-weight', '600')
            .style('font-size', '0.9rem')
            .text('Total Flights (Log Scale)')
          
          // Y Axis
          svg.append('g').call(d3.axisLeft(yScale).ticks(6))
          
          svg.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('y', -55)
            .attr('x', -height / 2)
            .attr('text-anchor', 'middle')
            .style('font-weight', '600')
            .style('font-size', '0.9rem')
            .text('Average Delay (minutes)')
          
          loading.value = false
        } catch (err) {
          console.error('Error drawing bubble chart:', err)
          loading.value = false
        }
      }
  
      watch(() => props.selectedState, drawChart)
  
      onMounted(drawChart)
  
      return { chartId, loading }
    }
  }
  </script>
  
  <style scoped>
  .chart-viz {
    width: 100%;
    min-height: 450px;
    position: relative;
  }
  
  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 450px;
    gap: 15px;
  }
  
  :deep(.bubble) {
    transition: all 0.2s;
  }
  
  :deep(.bubble.selected) {
    stroke: #ff6b6b !important;
    stroke-width: 3 !important;
  }
  </style>