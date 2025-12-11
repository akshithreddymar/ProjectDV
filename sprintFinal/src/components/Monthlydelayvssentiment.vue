<template>
    <div class="monthly-sentiment-container">
      <div :id="chartId" class="chart-viz"></div>
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <span>Loading seasonal patterns...</span>
      </div>
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
        <button @click="retryLoad" class="retry-btn">Retry</button>
      </div>
      
      <!-- Seasonal Insights -->
      <div v-if="seasonalInsights && !loading && !errorMessage" class="insight-box">
        <div class="insight-row">
          <div class="insight-item best">
            <div class="insight-icon">🌟</div>
            <div class="insight-content">
              <div class="insight-title">Best Month</div>
              <div class="insight-value">{{ seasonalInsights.bestMonth }}</div>
              <div class="insight-detail">{{ seasonalInsights.bestDelay }}% delays, {{ seasonalInsights.bestRating }} rating</div>
            </div>
          </div>
          <div class="insight-item worst">
            <div class="insight-icon">⚠️</div>
            <div class="insight-content">
              <div class="insight-title">Worst Month</div>
              <div class="insight-value">{{ seasonalInsights.worstMonth }}</div>
              <div class="insight-detail">{{ seasonalInsights.worstDelay }}% delays, {{ seasonalInsights.worstRating }} rating</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, watch } from 'vue'
  import * as d3 from 'd3'
  import { getCachedData, filterDelayData, filterReviewData } from '@/utils/dataCache'
  
  export default {
    name: 'MonthlyDelayVsSentiment',
    props: {
      filters: {
        type: Object,
        default: () => ({})
      },
      brushedAirlines: {
        type: Array,
        default: () => []
      }
    },
    setup(props) {
      const chartId = 'monthly-sentiment-' + Math.random().toString(36).substr(2, 9)
      const loading = ref(true)
      const errorMessage = ref(null)
      const seasonalInsights = ref(null)
  
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  
      const retryLoad = () => {
        errorMessage.value = null
        createChart()
      }
  
      const createChart = async () => {
        try {
          loading.value = true
          errorMessage.value = null
          seasonalInsights.value = null
  
          console.log('MonthlyDelayVsSentiment: Loading data...')
  
          // Get cached data
          const cachedData = await getCachedData()
          if (!cachedData || !cachedData.delays || !cachedData.reviews) {
            throw new Error('Data not available. Please ensure CSV files are loaded.')
          }
  
          const { delays, reviews } = cachedData
          console.log(`MonthlyDelayVsSentiment: Got ${delays.length} delays, ${reviews.length} reviews`)
  
          // Create custom filters - IGNORE state and airport for sentiment analysis
          const sentimentFilters = {
            selectedCarrier: props.filters.selectedCarrier,
            selectedDelayType: props.filters.selectedDelayType,
            yearStart: props.filters.yearStart,
            yearEnd: props.filters.yearEnd
            // Explicitly NOT including: selectedState, selectedAirport
          }
  
          // Apply filters (without state/airport)
          let filteredDelays = filterDelayData(delays, sentimentFilters)
          let filteredReviews = filterReviewData(reviews, sentimentFilters)
  
          console.log(`MonthlyDelayVsSentiment: After filters - ${filteredDelays.length} delays, ${filteredReviews.length} reviews`)
  
          // Apply brushed airlines filter if active
          if (props.brushedAirlines && props.brushedAirlines.length > 0) {
            console.log('MonthlyDelayVsSentiment: Applying brush filter for', props.brushedAirlines)
            
            filteredDelays = filteredDelays.filter(d => 
              props.brushedAirlines.includes(d.carrier_name)
            )
            
            filteredReviews = filteredReviews.filter(r => {
              return props.brushedAirlines.some(airline => {
                const reviewAirline = (r.airline_name || '').toLowerCase()
                const brushedAirline = airline.toLowerCase()
                return reviewAirline.includes(brushedAirline) || brushedAirline.includes(reviewAirline)
              })
            })
  
            console.log(`MonthlyDelayVsSentiment: After brush - ${filteredDelays.length} delays, ${filteredReviews.length} reviews`)
          }
  
          if (filteredDelays.length === 0) {
            errorMessage.value = 'No delay data available for the selected filters'
            loading.value = false
            return
          }
  
          // Aggregate by month
          const monthlyData = Array.from({ length: 12 }, (_, i) => ({
            month: i + 1,
            monthName: monthNames[i],
            flights: 0,
            delays: 0,
            ratings: [],
            reviewCount: 0
          }))
  
          // Process delays
          filteredDelays.forEach(row => {
            const month = +row.month
            if (month < 1 || month > 12) return
  
            const monthData = monthlyData[month - 1]
            monthData.flights += +(row.arr_flights || 0)
            monthData.delays += +(row.arr_del15 || 0)
          })
  
          // Process reviews
          filteredReviews.forEach(review => {
            try {
              const dateStr = review.date
              if (!dateStr) return
  
              const date = new Date(dateStr)
              if (isNaN(date.getTime())) return
  
              const month = date.getMonth() + 1
              if (month < 1 || month > 12) return
  
              const monthData = monthlyData[month - 1]
              const rating = parseFloat(review.overall_rating)
              if (!isNaN(rating) && rating > 0 && rating <= 10) {
                monthData.ratings.push(rating)
                monthData.reviewCount++
              }
            } catch (e) {
              // Skip invalid reviews
            }
          })
  
          // Calculate rates
          const processedData = monthlyData.map(d => ({
            ...d,
            delayRate: d.flights > 0 ? (d.delays / d.flights) * 100 : 0,
            avgRating: d.ratings.length > 0 ? d3.mean(d.ratings) : 0
          }))
  
          console.log('MonthlyDelayVsSentiment: Processed data', processedData)
  
          // Calculate insights
          const validMonths = processedData.filter(d => d.delayRate > 0 && d.avgRating > 0)
          if (validMonths.length >= 2) {
            const sortedByPerformance = [...validMonths].sort((a, b) => {
              const scoreA = a.avgRating - (a.delayRate / 10)
              const scoreB = b.avgRating - (b.delayRate / 10)
              return scoreB - scoreA
            })
            
            const bestMonth = sortedByPerformance[0]
            const worstMonth = sortedByPerformance[sortedByPerformance.length - 1]
  
            seasonalInsights.value = {
              bestMonth: bestMonth.monthName,
              bestDelay: bestMonth.delayRate.toFixed(1),
              bestRating: bestMonth.avgRating.toFixed(1),
              worstMonth: worstMonth.monthName,
              worstDelay: worstMonth.delayRate.toFixed(1),
              worstRating: worstMonth.avgRating.toFixed(1)
            }
          }
  
          drawChart(processedData)
          loading.value = false
        } catch (err) {
          console.error('MonthlyDelayVsSentiment error:', err)
          errorMessage.value = err.message || 'Failed to load seasonal data'
          loading.value = false
        }
      }
  
      const drawChart = (data) => {
        const container = document.getElementById(chartId)
        if (!container) {
          console.error('Container not found:', chartId)
          return
        }
  
        d3.select(`#${chartId}`).selectAll('*').remove()
  
        const margin = { top: 40, right: 70, bottom: 60, left: 60 }
        const width = container.clientWidth - margin.left - margin.right
        const height = 380 - margin.top - margin.bottom
  
        if (width <= 0 || height <= 0) {
          console.error('Invalid dimensions:', width, height)
          return
        }
  
        // Create SVG
        const svg = d3.select(`#${chartId}`)
          .append('svg')
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)
          .append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`)
  
        // Scales
        const xScale = d3.scaleBand()
          .domain(data.map(d => d.monthName))
          .range([0, width])
          .padding(0.2)
  
        const maxDelay = d3.max(data, d => d.delayRate) || 100
        const yScaleLeft = d3.scaleLinear()
          .domain([0, maxDelay * 1.1])
          .range([height, 0])
          .nice()
  
        const yScaleRight = d3.scaleLinear()
          .domain([0, 10])
          .range([height, 0])
  
        // Add grid lines
        svg.append('g')
          .attr('class', 'grid')
          .selectAll('line')
          .data(yScaleLeft.ticks(5))
          .enter()
          .append('line')
          .attr('x1', 0)
          .attr('x2', width)
          .attr('y1', d => yScaleLeft(d))
          .attr('y2', d => yScaleLeft(d))
          .attr('stroke', 'rgba(100, 116, 139, 0.1)')
          .attr('stroke-dasharray', '2,2')
  
        // Draw bars (delay rate)
        svg.selectAll('.bar')
          .data(data)
          .enter()
          .append('rect')
          .attr('class', 'bar')
          .attr('x', d => xScale(d.monthName))
          .attr('y', d => yScaleLeft(d.delayRate))
          .attr('width', xScale.bandwidth())
          .attr('height', d => height - yScaleLeft(d.delayRate))
          .attr('fill', 'rgba(239, 68, 68, 0.6)')
          .attr('stroke', '#ef4444')
          .attr('stroke-width', 1)
          .style('cursor', 'pointer')
          .on('mouseover', function(event, d) {
            d3.select(this)
              .attr('fill', 'rgba(239, 68, 68, 0.9)')
            showTooltip(event, d)
          })
          .on('mouseout', function() {
            d3.select(this)
              .attr('fill', 'rgba(239, 68, 68, 0.6)')
            hideTooltip()
          })
  
        // Draw line (average rating)
        const line = d3.line()
          .x(d => xScale(d.monthName) + xScale.bandwidth() / 2)
          .y(d => yScaleRight(d.avgRating))
          .curve(d3.curveMonotoneX)
  
        const dataWithRatings = data.filter(d => d.avgRating > 0)
  
        if (dataWithRatings.length > 0) {
          svg.append('path')
            .datum(dataWithRatings)
            .attr('class', 'line')
            .attr('d', line)
            .attr('fill', 'none')
            .attr('stroke', '#10b981')
            .attr('stroke-width', 3)
  
          // Add dots
          svg.selectAll('.dot')
            .data(dataWithRatings)
            .enter()
            .append('circle')
            .attr('class', 'dot')
            .attr('cx', d => xScale(d.monthName) + xScale.bandwidth() / 2)
            .attr('cy', d => yScaleRight(d.avgRating))
            .attr('r', 5)
            .attr('fill', '#10b981')
            .attr('stroke', '#0a0e27')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer')
            .on('mouseover', function(event, d) {
              d3.select(this).attr('r', 7)
              showTooltip(event, d)
            })
            .on('mouseout', function() {
              d3.select(this).attr('r', 5)
              hideTooltip()
            })
        }
  
        // X Axis
        svg.append('g')
          .attr('transform', `translate(0,${height})`)
          .call(d3.axisBottom(xScale))
          .attr('color', '#64748b')
          .selectAll('text')
          .attr('fill', '#cbd5e1')
          .attr('font-size', '11px')
  
        // Y Axis Left (Delay Rate)
        svg.append('g')
          .call(d3.axisLeft(yScaleLeft).ticks(5))
          .attr('color', '#64748b')
          .selectAll('text')
          .attr('fill', '#ef4444')
          .attr('font-size', '11px')
  
        // Y Axis Right (Rating)
        svg.append('g')
          .attr('transform', `translate(${width},0)`)
          .call(d3.axisRight(yScaleRight).ticks(5))
          .attr('color', '#64748b')
          .selectAll('text')
          .attr('fill', '#10b981')
          .attr('font-size', '11px')
  
        // Axis labels
        svg.append('text')
          .attr('x', width / 2)
          .attr('y', height + 45)
          .attr('text-anchor', 'middle')
          .attr('fill', '#e0e7ff')
          .attr('font-size', '13px')
          .attr('font-weight', '600')
          .text('Month')
  
        svg.append('text')
          .attr('transform', 'rotate(-90)')
          .attr('x', -height / 2)
          .attr('y', -45)
          .attr('text-anchor', 'middle')
          .attr('fill', '#ef4444')
          .attr('font-size', '13px')
          .attr('font-weight', '600')
          .text('Delay Rate (%)')
  
        svg.append('text')
          .attr('transform', 'rotate(-90)')
          .attr('x', -height / 2)
          .attr('y', width + 60)
          .attr('text-anchor', 'middle')
          .attr('fill', '#10b981')
          .attr('font-size', '13px')
          .attr('font-weight', '600')
          .text('Avg Rating (1-10)')
  
        // Legend
        const legend = svg.append('g')
          .attr('class', 'legend')
          .attr('transform', `translate(${width / 2 - 100}, -25)`)
  
        legend.append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('width', 18)
          .attr('height', 12)
          .attr('fill', 'rgba(239, 68, 68, 0.6)')
  
        legend.append('text')
          .attr('x', 22)
          .attr('y', 9)
          .attr('fill', '#cbd5e1')
          .attr('font-size', '11px')
          .text('Delay Rate')
  
        legend.append('line')
          .attr('x1', 110)
          .attr('x2', 128)
          .attr('y1', 6)
          .attr('y2', 6)
          .attr('stroke', '#10b981')
          .attr('stroke-width', 3)
  
        legend.append('circle')
          .attr('cx', 119)
          .attr('cy', 6)
          .attr('r', 4)
          .attr('fill', '#10b981')
  
        legend.append('text')
          .attr('x', 132)
          .attr('y', 9)
          .attr('fill', '#cbd5e1')
          .attr('font-size', '11px')
          .text('Avg Rating')
      }
  
      let tooltip
      const showTooltip = (event, d) => {
        if (!d || typeof d !== 'object') {
          console.warn('Invalid tooltip data:', d)
          return
        }
  
        if (!tooltip) {
          tooltip = d3.select('body').append('div')
            .attr('class', 'chart-tooltip')
            .style('opacity', 0)
            .style('position', 'absolute')
            .style('background', 'rgba(10, 14, 39, 0.95)')
            .style('border', '1px solid rgba(0, 240, 255, 0.5)')
            .style('border-radius', '8px')
            .style('padding', '12px')
            .style('pointer-events', 'none')
            .style('color', '#e0e7ff')
            .style('font-size', '12px')
            .style('backdrop-filter', 'blur(10px)')
            .style('z-index', '1000')
        }
  
        tooltip.transition().duration(200).style('opacity', 1)
        tooltip.html(`
          <div style="font-weight: 700; color: #00f0ff; margin-bottom: 8px;">${d.monthName || 'Unknown'}</div>
          <div style="margin-bottom: 4px;"><strong>Total Flights:</strong> ${(d.flights || 0).toLocaleString()}</div>
          <div style="margin-bottom: 4px;"><strong>Delay Rate:</strong> ${(d.delayRate || 0).toFixed(2)}%</div>
          <div style="margin-bottom: 4px;"><strong>Avg Rating:</strong> ${d.avgRating > 0 ? d.avgRating.toFixed(1) : 'N/A'}</div>
          <div style="margin-bottom: 4px;"><strong>Reviews:</strong> ${d.reviewCount || 0}</div>
        `)
          .style('left', (event.pageX + 15) + 'px')
          .style('top', (event.pageY - 15) + 'px')
      }
  
      const hideTooltip = () => {
        if (tooltip) {
          tooltip.transition().duration(200).style('opacity', 0)
        }
      }
  
      watch(() => [props.filters, props.brushedAirlines], () => {
        console.log('MonthlyDelayVsSentiment: Filters or brush changed, reloading...')
        createChart()
      }, { deep: true })
  
      onMounted(() => {
        createChart()
        window.addEventListener('resize', createChart)
      })
  
      return {
        chartId,
        loading,
        errorMessage,
        seasonalInsights,
        retryLoad
      }
    }
  }
  </script>
  
  <style scoped>
  .monthly-sentiment-container {
    position: relative;
    width: 100%;
    min-height: 500px;
  }
  
  .chart-viz {
    width: 100%;
    min-height: 420px;
  }
  
  .loading-overlay {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    color: #cbd5e1;
    font-size: 0.9rem;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(0, 240, 255, 0.1);
    border-top-color: #00f0ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .error-message {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #ef4444;
    font-size: 0.95rem;
    text-align: center;
    padding: 20px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    max-width: 80%;
  }
  
  .retry-btn {
    margin-top: 12px;
    padding: 8px 16px;
    background: rgba(0, 240, 255, 0.2);
    border: 1px solid #00f0ff;
    color: #00f0ff;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.3s ease;
  }
  
  .retry-btn:hover {
    background: rgba(0, 240, 255, 0.3);
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
  }
  
  .insight-box {
    margin-top: 20px;
    padding: 16px;
    background: rgba(10, 14, 39, 0.5);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 8px;
  }
  
  .insight-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  
  .insight-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 6px;
  }
  
  .insight-item.best {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
  }
  
  .insight-item.worst {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
  }
  
  .insight-icon {
    font-size: 2rem;
  }
  
  .insight-content {
    flex: 1;
  }
  
  .insight-title {
    font-size: 0.75rem;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
  }
  
  .insight-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e0e7ff;
    margin-bottom: 4px;
  }
  
  .insight-detail {
    font-size: 0.85rem;
    color: #cbd5e1;
  }
  </style>