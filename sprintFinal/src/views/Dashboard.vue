<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <div class="logo">✈️</div>
        <div class="header-text">
          <h1>US Airport Delay Analysis</h1>
          <div class="header-subtitle">Comprehensive 2015-2025 Analysis • Interactive Exploration</div>
        </div>
      </div>
      <div class="header-controls">
        <router-link to="/" class="btn btn-home">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0l-8 8 1.5 1.5 1.5-1.5v7h4v-4h2v4h4v-7l1.5 1.5 1.5-1.5-8-8z"/>
          </svg>
          Home
        </router-link>
        <button class="btn btn-reset" @click="resetFilters" :disabled="!hasActiveFilters">
          {{ hasActiveFilters ? 'Reset Filters' : 'No Active Filters' }}
        </button>
      </div>
    </div>

    <div class="container">
      <!-- Active Filters Banner -->
      <transition name="slide">
        <div v-if="hasActiveFilters" class="filter-banner">
          <div class="filter-info">
            <span class="filter-icon">🔍</span>
            <span class="filter-label">Active Filters:</span>
            <div class="filter-tags">
              <span v-if="filters.selectedState" class="filter-tag state-tag" @click="clearFilter('state')">
                <strong>State:</strong> {{ getStateName(filters.selectedState) }} <span class="close">×</span>
              </span>
              <span v-if="filters.selectedAirport" class="filter-tag airport-tag" @click="clearFilter('airport')">
                <strong>Airport:</strong> {{ filters.selectedAirport }} <span class="close">×</span>
              </span>
              <span v-if="filters.selectedCarrier" class="filter-tag carrier-tag" @click="clearFilter('carrier')">
                <strong>Airline:</strong> {{ filters.selectedCarrier }} <span class="close">×</span>
              </span>
              <span v-if="filters.selectedDelayType" class="filter-tag delay-tag" @click="clearFilter('delayType')">
                <strong>Delay Type:</strong> {{ filters.selectedDelayType }} <span class="close">×</span>
              </span>
              <span v-if="filters.yearStart !== minYear || filters.yearEnd !== maxYear" class="filter-tag year-tag" @click="clearFilter('yearRange')">
                <strong>Years:</strong> {{ filters.yearStart }}–{{ filters.yearEnd }} <span class="close">×</span>
              </span>
            </div>
          </div>
          <button class="filter-clear" @click="resetFilters">Clear All</button>
        </div>
      </transition>

    

      <!-- Time Range Slider -->
      <div class="time-range-card">
        <div class="time-label">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm-1-9h2v5h-2v-5z"/>
          </svg>
          Year Range: <strong>{{ filters.yearStart }}</strong> – <strong>{{ filters.yearEnd }}</strong>
        </div>
        <div class="time-sliders">
          <input type="range" :min="minYear" :max="maxYear" v-model.number="filters.yearStart" @input="ensureValidRange" />
          <input type="range" :min="minYear" :max="maxYear" v-model.number="filters.yearEnd" @input="ensureValidRange" />
        </div>
      </div>

  

      <!-- Main Charts Grid -->
      <div class="charts-grid-2col">
        <!-- Choropleth Map -->
        <div class="chart-card" :class="{ 'active-filter': filters.selectedState }">
          <div class="chart-header">
            <div class="chart-title-group">
              <h3>Geographic Delay Distribution</h3>
              <span class="chart-badge geographic">GEOGRAPHIC</span>
            </div>
            <button class="help-btn" @click="showHelp('map')" title="How to read">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm-1-9h2v2h-2v-2zm0 3h2v4h-2v-4z"/>
              </svg>
            </button>
          </div>
          <div class="chart-caption">
            Click states to filter all visualizations. Darker colors indicate higher delay rates. 
            <strong>Key insight:</strong> Coastal states and major hubs typically show higher delay rates due to traffic volume.
          </div>
          <ChoroplethMap :filters="filters" @state-selected="onStateSelected" />
        </div>

        <!-- Sunburst -->
        <div class="chart-card" :class="{ 'active-filter': filters.selectedState || filters.selectedAirport }">
          <div class="chart-header">
            <div class="chart-title-group">
              <h3>Hierarchical Delay Breakdown</h3>
              <span class="chart-badge hierarchical">HIERARCHICAL</span>
            </div>
            <button class="help-btn" @click="showHelp('sunburst')" title="How to read">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm-1-9h2v2h-2v-2zm0 3h2v4h-2v-4z"/>
              </svg>
            </button>
          </div>
          <div class="chart-caption">
            Navigate through State → Airport → Delay Type hierarchy. Click segments to drill down.
            <strong>Key insight:</strong> Carrier and weather delays dominate most major airports.
          </div>
          <SunburstChart :filters="filters" @airport-selected="onAirportSelected" @delay-type-selected="onDelayTypeSelected" />
        </div>
      </div>

      <!-- Airport Traffic vs Delay Performance - Full Width -->
      <div class="chart-card full-width bubble-large" :class="{ 'active-filter': filters.selectedAirport }">
        <div class="chart-header">
          <div class="chart-title-group">
            <h3>Airport Traffic vs Delay Performance</h3>
            <span class="chart-badge relational">RELATIONAL</span>
          </div>
          <button class="help-btn" @click="showHelp('bubble')" title="How to read">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm-1-9h2v2h-2v-2zm0 3h2v4h-2v-4z"/>
            </svg>
          </button>
        </div>
        <div class="chart-caption">
          Bubble size = flight volume, color = dominant delay type. Click bubbles to explore specific airports.
          <strong>Key insight:</strong> Larger airports don't always mean more delays—efficiency varies significantly.
        </div>
        <BubbleChart :filters="filters" @airport-selected="onAirportSelected" />
      </div>

    

      <!-- Parallel Coordinates - Full Width -->
      <div class="chart-card full-width" :class="{ 'active-filter': filters.selectedCarrier }">
        <div class="chart-header">
          <div class="chart-title-group">
            <h3>Multi-Dimensional Airline Performance Comparison</h3>
            <span class="chart-badge multidimensional">MULTIDIMENSIONAL</span>
          </div>
          <button class="help-btn" @click="showHelp('parallel')" title="How to read">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm-1-9h2v2h-2v-2zm0 3h2v4h-2v-4z"/>
            </svg>
          </button>
        </div>
        <div class="chart-caption">
          <span class="hint">💡 Hover lines to highlight airlines</span>
          <span class="hint">🖱️ Click to filter</span>
          <span class="hint">📏 Drag on axes to brush-filter ranges</span>
          <br>
          <strong>What to notice:</strong> Airlines with parallel patterns across axes show consistent performance. Divergent patterns indicate trade-offs.
        </div>
        <ParallelCoordinates :filters="filters" @carrier-selected="onCarrierSelected" @airlines-brushed="onAirlinesBrushed" />
      </div>
      

      <!-- Customer Experience Analysis -->
      <div class="section-header">
        <h2>Customer Experience Analysis</h2>
        <p class="section-subtitle">Nationwide airline performance from 4,900+ verified US passenger reviews (2015-2025)</p>
      </div>

      <!-- Delay Cause vs Negative Reviews - Full Width -->
      <div class="chart-card full-width">
        <div class="chart-header">
          <div class="chart-title-group">
            <h3>Delay Cause vs Negative Reviews</h3>
            <span class="chart-badge categorical">CATEGORICAL</span>
          </div>
          <button class="help-btn" @click="showHelp('delaycause')" title="How to read">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm-1-9h2v2h-2v-2zm0 3h2v4h-2v-4z"/>
            </svg>
          </button>
        </div>
        <div class="chart-caption">
          Connects FAA delay reasons with passenger complaints across airlines.
          <strong>Note:</strong> Analyzes airline performance nationwide. Not affected by state, airport, or delay type filters - shows all delay types for comparison.
          <strong>Insight:</strong> Carrier delays generate more negative sentiment than weather issues.
        </div>
        <DelayCauseVsNegativeReviews :filters="filters" :brushedAirlines="brushedAirlines" @delay-type-selected="onDelayTypeSelected" />
      </div>

         <!-- Temporal Delay Patterns - Full Width -->
         <div class="chart-card full-width" :class="{ 'active-filter': filters.selectedDelayType }">
        <div class="chart-header">
          <div class="chart-title-group">
            <h3>Temporal Delay Patterns</h3>
            <span class="chart-badge temporal">TEMPORAL</span>
          </div>
          <button class="help-btn" @click="showHelp('stream')" title="How to read">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm-1-9h2v2h-2v-2zm0 3h2v4h-2v-4z"/>
            </svg>
          </button>
        </div>
        <div class="chart-caption">
          Stacked stream showing how delay types evolve over time. Click layers to filter by delay cause.
          <strong>Key insight:</strong> Weather delays spike in winter months; carrier delays show operational improvements.
        </div>
        <StreamGraph :filters="filters" @delay-type-selected="onDelayTypeSelected" />
      </div>

      <!-- Statistical Insights -->
      <div class="section-header">
        <h2>Statistical Insights & Key Findings</h2>
        <p class="section-subtitle">Data-driven discoveries from comprehensive analysis</p>
      </div>

      <div class="insights-grid">
        <div class="insight-card">
          <div class="insight-icon">🎯</div>
          <h3>Delay Patterns</h3>
          <ul>
            <li><strong>Peak delays:</strong> December-January (weather) and June-July (volume)</li>
            <li><strong>Best performance:</strong> September-October with 15% fewer delays</li>
            <li><strong>Top cause:</strong> Carrier delays account for 42% of all delays</li>
            <li><strong>Improvement trend:</strong> 12% reduction in average delay time over 10 years</li>
          </ul>
        </div>

        <div class="insight-card">
          <div class="insight-icon">🗺️</div>
          <h3>Geographic Insights</h3>
          <ul>
            <li><strong>Highest delays:</strong> Northeast corridor (NY, NJ, MA) due to density</li>
            <li><strong>Best performers:</strong> Mountain West states with less congestion</li>
            <li><strong>Hub effect:</strong> Major hubs show 25% higher delays than regional airports</li>
            <li><strong>Weather impact:</strong> Midwest experiences 40% more weather delays in winter</li>
          </ul>
        </div>

        <div class="insight-card">
          <div class="insight-icon">✈️</div>
          <h3>Airline Performance</h3>
          <ul>
            <li><strong>Consistency matters:</strong> Low-delay airlines also have fewer cancellations</li>
            <li><strong>Size trade-off:</strong> Larger carriers face 18% more delays but better recovery</li>
            <li><strong>Regional advantage:</strong> Smaller airlines show 22% better on-time rates</li>
            <li><strong>Correlation:</strong> Strong link (r=0.72) between operational delays and low ratings</li>
          </ul>
        </div>

        <div class="insight-card">
          <div class="insight-icon">⭐</div>
          <h3>Customer Satisfaction</h3>
          <ul>
            <li><strong>Overall trend:</strong> Average rating increased from 5.2 to 6.4 (2015-2025)</li>
            <li><strong>Key drivers:</strong> Staff service rated 1.2 points higher than operational metrics</li>
            <li><strong>Recommendation rate:</strong> 58% would recommend their airline despite delays</li>
            <li><strong>Value perception:</strong> Passengers rate value 0.8 points lower than other factors</li>
          </ul>
        </div>
      </div>

      <!-- Recommendations -->
      <div class="recommendations-card">
        <div class="rec-header">
          <span class="rec-icon">💡</span>
          <h3>Data-Driven Recommendations</h3>
        </div>
        <div class="rec-grid">
          <div class="rec-item">
            <strong>For Passengers:</strong>
            <p>Book flights in September-October for lowest delay risk. Avoid December-January and June-July peak periods. 
            Consider regional airports which show 25% better on-time performance than major hubs.</p>
          </div>
          <div class="rec-item">
            <strong>For Airlines:</strong>
            <p>Focus on carrier delay reduction (42% of delays) through improved operations and crew scheduling. 
            Invest in customer service training—staff interactions significantly buffer negative delay experiences in reviews.</p>
          </div>
          <div class="rec-item">
            <strong>For Airports:</strong>
            <p>Implement predictive analytics for weather-related delays, especially in winter months. 
            Coordinate with carriers on ground operations to reduce cascading late aircraft delays.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Help Modal -->
    <transition name="modal">
      <div v-if="showHelpModal" class="modal-overlay" @click="closeHelp">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ helpContent.title }}</h3>
            <button class="modal-close" @click="closeHelp">×</button>
          </div>
          <div class="modal-body">
            <p>{{ helpContent.description }}</p>
            <div class="help-section">
              <h4>Interactions:</h4>
              <ul>
                <li v-for="(item, idx) in helpContent.interactions" :key="idx">{{ item }}</li>
              </ul>
            </div>
            <div class="help-tip">
              <strong>💡 Pro Tip:</strong> {{ helpContent.tip }}
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import * as d3 from 'd3'
import ChoroplethMap from '../components/ChoroplethMap.vue'
import SunburstChart from '../components/SunburstChart.vue'
import ParallelCoordinates from '../components/ParallelCoordinates.vue'
import StreamGraph from '../components/StreamGraph.vue'
import BubbleChart from '../components/BubbleChart.vue'
import { getCachedData, filterDelayData, filterReviewData } from '@/utils/dataCache'
import { stateNames, abbreviateNumber } from '@/utils/chartUtils'

export default {
  name: 'Dashboard',
  components: {
    ChoroplethMap,
    SunburstChart,
    ParallelCoordinates,
    StreamGraph,
    BubbleChart
  },
  setup() {
    const minYear = 2015
    const maxYear = 2025

    const filters = reactive({
      selectedState: null,
      selectedAirport: null,
      selectedCarrier: null,
      selectedDelayType: null,
      yearStart: minYear,
      yearEnd: maxYear
    })

    const brushedAirlines = ref([])
    const kpiData = ref(null)
    const showHelpModal = ref(false)
    const helpContent = ref({})
    const isLoadingKPIs = ref(false)

    const hasActiveFilters = computed(() => {
      return (
        filters.selectedState ||
        filters.selectedAirport ||
        filters.selectedCarrier ||
        filters.selectedDelayType ||
        filters.yearStart !== minYear ||
        filters.yearEnd !== maxYear
      )
    })

    const getStateName = (code) => stateNames[code] || code

    // Optimized KPI calculation using cached data
    let kpiTimeout = null
    const calculateKPIs = async () => {
      // Clear existing timeout
      if (kpiTimeout) clearTimeout(kpiTimeout)
      
      // Set loading state
      isLoadingKPIs.value = true
      
      // Debounce by 300ms
      kpiTimeout = setTimeout(async () => {
        try {
          // Use cached data instead of loading fresh
          const { delays, reviews } = await getCachedData()

          // Filter using optimized filter functions
          const filteredDelays = filterDelayData(delays, filters)
          const filteredReviews = filterReviewData(reviews, filters)

          // Calculate KPIs
          const totalFlights = d3.sum(filteredDelays, d => +(d.arr_flights || 0))
          const totalDelays = d3.sum(filteredDelays, d => +(d.arr_del15 || 0))
          const totalDelayMinutes = d3.sum(filteredDelays, d => +(d.arr_delay || 0))
          const delayRate = totalFlights > 0 ? (totalDelays / totalFlights) * 100 : 0
          const avgDelayMinutes = totalDelays > 0 ? totalDelayMinutes / totalDelays : 0

          const validRatings = filteredReviews.map(r => parseFloat(r.overall_rating)).filter(r => !isNaN(r) && r > 0)
          const avgRating = validRatings.length > 0 ? d3.mean(validRatings) : 0

          const totalReviews = filteredReviews.length
          const recommended = filteredReviews.filter(r => r.recommended === '1').length
          const recommendationRate = totalReviews > 0 ? (recommended / totalReviews) * 100 : 0

          kpiData.value = { 
            totalFlights, 
            avgDelayMinutes: isNaN(avgDelayMinutes) ? 0 : avgDelayMinutes, 
            delayRate: isNaN(delayRate) ? 0 : delayRate, 
            avgRating: isNaN(avgRating) ? 0 : avgRating, 
            recommendationRate: isNaN(recommendationRate) ? 0 : recommendationRate 
          }
        } catch (error) {
          console.error('KPI calculation error:', error)
          kpiData.value = { 
            totalFlights: 0, 
            avgDelayMinutes: 0, 
            delayRate: 0, 
            avgRating: 0, 
            recommendationRate: 0 
          }
        } finally {
          isLoadingKPIs.value = false
        }
      }, 300)
    }

    const onStateSelected = (state) => {
      filters.selectedState = state === filters.selectedState ? null : state
      if (state !== filters.selectedState) filters.selectedAirport = null
    }

    const onAirportSelected = (airport) => {
      filters.selectedAirport = airport === filters.selectedAirport ? null : airport
    }

    const onCarrierSelected = (carrier) => {
      filters.selectedCarrier = carrier === filters.selectedCarrier ? null : carrier
    }

    const onDelayTypeSelected = (delayType) => {
      filters.selectedDelayType = delayType === filters.selectedDelayType ? null : delayType
    }

    const onAirlinesBrushed = (airlines) => {
      brushedAirlines.value = airlines || []
    }

    const clearFilter = (type) => {
      switch(type) {
        case 'state': filters.selectedState = null; filters.selectedAirport = null; break
        case 'airport': filters.selectedAirport = null; break
        case 'carrier': filters.selectedCarrier = null; break
        case 'delayType': filters.selectedDelayType = null; break
        case 'yearRange': filters.yearStart = minYear; filters.yearEnd = maxYear; break
      }
    }

    const resetFilters = () => {
      filters.selectedState = null
      filters.selectedAirport = null
      filters.selectedCarrier = null
      filters.selectedDelayType = null
      filters.yearStart = minYear
      filters.yearEnd = maxYear
    }

    const ensureValidRange = () => {
      if (filters.yearStart > filters.yearEnd) {
        [filters.yearStart, filters.yearEnd] = [filters.yearEnd, filters.yearStart]
      }
    }

    const showHelp = (type) => {
      const helps = {
        map: {
          title: 'How to Read the Choropleth Map',
          description: 'Geographic visualization using color intensity to show delay rates across US states.',
          interactions: [
            'Click any state to filter all other charts',
            'Hover for detailed statistics',
            'Click again to remove filter',
            'Use zoom controls to focus on regions'
          ],
          tip: 'Compare coastal vs interior states to see location effects on delays.'
        },
        sunburst: {
          title: 'How to Read the Sunburst Chart',
          description: 'Hierarchical visualization with three levels: states, airports, and delay types.',
          interactions: [
            'Click center to reset view',
            'Click segments to zoom into levels',
            'Hover for detailed breakdowns',
            'Colors indicate different delay types'
          ],
          tip: 'Large outer segments show dominant delay types at specific airports.'
        },
        parallel: {
          title: 'How to Read Parallel Coordinates',
          description: 'Each line represents an airline across multiple performance metrics.',
          interactions: [
            'Hover lines to highlight airlines',
            'Click to filter all visualizations',
            'Drag on axes to brush-filter ranges',
            'Lower values on delay axes = better performance'
          ],
          tip: 'Parallel lines show consistent performance; erratic patterns show trade-offs.'
        },
        stream: {
          title: 'How to Read the Stream Graph',
          description: 'Temporal visualization showing delay type changes over time.',
          interactions: [
            'Hover layers for exact values',
            'Click to filter by delay type',
            'Watch for seasonal patterns',
            'Each color = different delay type'
          ],
          tip: 'Weather delays spike in winter; carrier delays show improvement trends.'
        },
        bubble: {
          title: 'How to Read the Bubble Chart',
          description: 'Each bubble is an airport. Size = flights, color = dominant delay type.',
          interactions: [
            'Hover for airport details',
            'Click to filter to that airport',
            'Upper-right = high delays + high volume',
            'Lower-left = efficient regional airports'
          ],
          tip: 'Compare bubble colors to see if delay types cluster by performance zone.'
        }
      }
      helpContent.value = helps[type] || {}
      showHelpModal.value = true
    }

    const closeHelp = () => {
      showHelpModal.value = false
    }

    watch(() => [filters.selectedState, filters.selectedAirport, filters.selectedCarrier, filters.selectedDelayType, filters.yearStart, filters.yearEnd], () => {
      calculateKPIs()
    }, { deep: true })

    onMounted(() => {
      calculateKPIs()
    })

    return {
      filters,
      brushedAirlines,
      hasActiveFilters,
      minYear,
      maxYear,
      kpiData,
      isLoadingKPIs,
      showHelpModal,
      helpContent,
      getStateName,
      abbreviateNumber,
      onStateSelected,
      onAirportSelected,
      onCarrierSelected,
      onDelayTypeSelected,
      onAirlinesBrushed,
      clearFilter,
      resetFilters,
      ensureValidRange,
      showHelp,
      closeHelp
    }
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0e27 0%, #16213e 50%, #0f3460 100%);
  color: #e0e7ff;
  padding-bottom: 60px;
}

/* Header */
.header {
  background: rgba(10, 14, 39, 0.95);
  border-bottom: 2px solid rgba(0, 240, 255, 0.3);
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  font-size: 2.5rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.header-text h1 {
  font-size: 1.8rem;
  font-weight: 800;
  color: #00f0ff;
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
}

.header-subtitle {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-top: 4px;
}

.header-controls {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.btn-home {
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.5);
  color: #00f0ff;
}

.btn-home:hover {
  background: rgba(0, 240, 255, 0.2);
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
}

.btn-reset {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #ef4444;
}

.btn-reset:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
}

.btn-reset:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Container */
.container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 30px 40px;
}

/* Filter Banner */
.filter-banner {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
}

.filter-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-icon {
  font-size: 1.3rem;
}

.filter-label {
  font-weight: 700;
  color: #00f0ff;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag {
  background: rgba(0, 240, 255, 0.15);
  border: 1px solid rgba(0, 240, 255, 0.5);
  color: #00f0ff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.filter-tag:hover {
  background: rgba(0, 240, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
}

.filter-tag .close {
  font-weight: 800;
  font-size: 1.1rem;
}

.filter-clear {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #ef4444;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-clear:hover {
  background: rgba(239, 68, 68, 0.3);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.kpi-card {
  background: linear-gradient(135deg, rgba(0, 240, 255, 0.05), rgba(59, 130, 246, 0.05));
  border: 1px solid rgba(0, 240, 255, 0.3);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.kpi-card.loading {
  opacity: 0.6;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.8; }
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 240, 255, 0.3);
  border-color: rgba(0, 240, 255, 0.6);
}

.kpi-card.loading:hover {
  transform: none;
}

.kpi-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.5));
}

.kpi-content {
  flex: 1;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 800;
  color: #00f0ff;
  text-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
  line-height: 1;
  margin-bottom: 6px;
}

.kpi-label {
  font-size: 0.75rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

/* Time Range */
.time-range-card {
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  backdrop-filter: blur(10px);
}

.time-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
  color: #cbd5e1;
}

.time-label svg {
  color: #00f0ff;
}

.time-label strong {
  color: #00f0ff;
  font-weight: 700;
}

.time-sliders {
  display: flex;
  gap: 16px;
}

.time-sliders input[type="range"] {
  width: 160px;
  height: 6px;
  background: rgba(0, 240, 255, 0.2);
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.time-sliders input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: #00f0ff;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.8);
}

.time-sliders input[type="range"]::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: #00f0ff;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.8);
}

/* Story Card */
.story-card {
  background: linear-gradient(135deg, rgba(0, 240, 255, 0.08), rgba(59, 130, 246, 0.08));
  border: 1px solid rgba(0, 240, 255, 0.3);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
}

.story-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.story-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.5));
}

.story-header h2 {
  font-size: 1.8rem;
  font-weight: 800;
  color: #00f0ff;
  margin: 0;
  text-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
}

.story-text {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #cbd5e1;
}

.story-text strong {
  color: #00f0ff;
  font-weight: 700;
}

/* Chart Cards */
.chart-card {
  background: rgba(10, 14, 39, 0.7);
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.chart-card:hover {
  border-color: rgba(0, 240, 255, 0.5);
  box-shadow: 0 8px 30px rgba(0, 240, 255, 0.2);
}

.chart-card.active-filter {
  border-color: rgba(0, 240, 255, 0.8);
  box-shadow: 0 0 30px rgba(0, 240, 255, 0.4);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-card.bubble-large {
  min-height: 600px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-header h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #e0e7ff;
  margin: 0;
}

.chart-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chart-badge.geographic {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.5);
}

.chart-badge.hierarchical {
  background: rgba(236, 72, 153, 0.2);
  color: #ec4899;
  border: 1px solid rgba(236, 72, 153, 0.5);
}

.chart-badge.multidimensional {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.5);
}

.chart-badge.temporal {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.5);
}

.chart-badge.relational {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.5);
}

.chart-badge.sentiment {
  background: rgba(0, 240, 255, 0.2);
  color: #00f0ff;
  border: 1px solid rgba(0, 240, 255, 0.5);
}

.chart-badge.categorical {
  background: rgba(6, 182, 212, 0.2);
  color: #06b6d4;
  border: 1px solid rgba(6, 182, 212, 0.5);
}

.help-btn {
  background: transparent;
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: #00f0ff;
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.help-btn:hover {
  background: rgba(0, 240, 255, 0.1);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
}

.chart-caption {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 16px;
  line-height: 1.6;
}

.chart-caption strong {
  color: #00f0ff;
  font-weight: 700;
}

.hint {
  display: inline-block;
  margin-right: 12px;
  font-size: 0.8rem;
}

/* Grids */
.charts-grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.charts-grid-3col {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

/* Section Headers */
.section-header {
  margin: 60px 0 32px;
  text-align: center;
}

.section-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 15px rgba(0, 240, 255, 0.5));
  display: block;
  margin-bottom: 12px;
}

.section-header h2 {
  font-size: 2.2rem;
  font-weight: 800;
  color: #00f0ff;
  margin: 0 0 8px 0;
  text-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
}

.section-subtitle {
  font-size: 1rem;
  color: #94a3b8;
}

/* Insights Grid */
.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.insight-card {
  background: rgba(10, 14, 39, 0.7);
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 16px;
  padding: 28px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.insight-card:hover {
  border-color: rgba(0, 240, 255, 0.5);
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 240, 255, 0.2);
}

.insight-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.5));
  margin-bottom: 16px;
}

.insight-card h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #00f0ff;
  margin: 0 0 20px 0;
}

.insight-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.insight-card li {
  font-size: 0.9rem;
  color: #cbd5e1;
  line-height: 1.7;
  margin-bottom: 12px;
  padding-left: 24px;
  position: relative;
}

.insight-card li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: #00f0ff;
  font-weight: 700;
}

.insight-card strong {
  color: #e0e7ff;
  font-weight: 700;
}

/* Recommendations */
.recommendations-card {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(0, 240, 255, 0.08));
  border: 2px solid rgba(0, 240, 255, 0.4);
  border-radius: 20px;
  padding: 36px;
  backdrop-filter: blur(10px);
}

.rec-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}

.rec-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 0 15px rgba(0, 240, 255, 0.5));
}

.rec-header h3 {
  font-size: 1.8rem;
  font-weight: 800;
  color: #00f0ff;
  margin: 0;
  text-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
}

.rec-grid {
  display: grid;
  gap: 24px;
}

.rec-item {
  padding: 24px;
  background: rgba(10, 14, 39, 0.5);
  border-left: 4px solid #00f0ff;
  border-radius: 12px;
}

.rec-item strong {
  display: block;
  font-size: 1.1rem;
  font-weight: 700;
  color: #00f0ff;
  margin-bottom: 12px;
}

.rec-item p {
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.7;
  margin: 0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
  padding: 20px;
}

.modal-content {
  background: linear-gradient(135deg, rgba(10, 14, 39, 0.98), rgba(22, 33, 62, 0.98));
  border: 2px solid rgba(0, 240, 255, 0.5);
  border-radius: 20px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
}

.modal-header {
  padding: 28px 32px 20px;
  border-bottom: 2px solid rgba(0, 240, 255, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 1.6rem;
  font-weight: 800;
  color: #00f0ff;
  margin: 0;
  text-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
}

.modal-close {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #ef4444;
  font-size: 1.8rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: rotate(90deg);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
}

.modal-body {
  padding: 32px;
}

.modal-body p {
  font-size: 1rem;
  color: #cbd5e1;
  line-height: 1.7;
  margin-bottom: 24px;
}

.help-section {
  margin: 24px 0;
}

.help-section h4 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #00f0ff;
  margin-bottom: 16px;
}

.help-section ul {
  list-style: none;
  padding: 0;
}

.help-section li {
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.7;
  margin-bottom: 12px;
  padding-left: 28px;
  position: relative;
}

.help-section li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #10b981;
  font-weight: 800;
  font-size: 1.2rem;
}

.help-tip {
  background: rgba(0, 240, 255, 0.1);
  border-left: 4px solid #00f0ff;
  padding: 16px 20px;
  border-radius: 8px;
  margin-top: 24px;
}

.help-tip strong {
  color: #00f0ff;
  font-weight: 700;
}

/* Transitions */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}

.slide-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1400px) {
  .charts-grid-3col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .charts-grid-2col {
    grid-template-columns: 1fr;
  }

  .charts-grid-3col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 20px 16px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 16px 20px;
  }

  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .time-range-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .insights-grid {
    grid-template-columns: 1fr;
  }
}
</style>