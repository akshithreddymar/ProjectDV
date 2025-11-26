<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="header">
      <div>
        <h1>US Airport Delay Analysis Dashboard</h1>
        <div class="header-subtitle">2015-2025 • Interactive Analysis • Cross-Chart Filtering</div>
      </div>
      <div class="header-controls">
        <router-link to="/" class="btn btn-secondary">← Back</router-link>
        <button class="btn btn-danger" @click="resetFilters" :disabled="!hasActiveFilters">
          <span v-if="hasActiveFilters">Reset Filters</span>
          <span v-else>No Active Filters</span>
        </button>
      </div>
    </div>

    <!-- Filter Banner -->
    <div class="container">
      <transition name="slide-fade">
        <div v-if="hasActiveFilters" class="filter-banner">
          <div class="filter-info">
            <span class="filter-icon">🔍</span>
            <span class="filter-label">Active Filters:</span>
            <div class="filter-tags">
              <span v-if="filters.selectedState" class="filter-tag state-tag" @click="clearFilter('state')">
                📍 {{ getStateName(filters.selectedState) }}
                <span class="tag-close">×</span>
              </span>
              <span v-if="filters.selectedAirport" class="filter-tag airport-tag" @click="clearFilter('airport')">
                🛫 {{ filters.selectedAirport }}
                <span class="tag-close">×</span>
              </span>
              <span v-if="filters.selectedCarrier" class="filter-tag carrier-tag" @click="clearFilter('carrier')">
                ✈️ {{ filters.selectedCarrier }}
                <span class="tag-close">×</span>
              </span>
              <span v-if="filters.selectedDelayType" class="filter-tag delay-tag" @click="clearFilter('delayType')">
                ⏱️ {{ filters.selectedDelayType }}
                <span class="tag-close">×</span>
              </span>
            </div>
          </div>
          <div class="filter-clear" @click="resetFilters">Clear All ✕</div>
        </div>
      </transition>

      <!-- Visualizations Grid -->
      <div class="dashboard-grid">
        <!-- Choropleth Map -->
        <div class="chart-container" :class="{ 'chart-filtered': filters.selectedState }">
          <div class="chart-header">
            <div class="chart-title">
              <span>Delay Rates by State</span>
            </div>
            <div class="chart-badge geographic">Geographic</div>
          </div>
          <div class="chart-description">Click on a state to filter all charts</div>
          <ChoroplethMap 
            :filters="filters"
            @state-selected="onStateSelected"
          />
        </div>

        <!-- Sunburst Chart -->
        <div class="chart-container" :class="{ 'chart-filtered': filters.selectedState }">
          <div class="chart-header">
            <div class="chart-title">
              <span>Delay Breakdown Hierarchy</span>
            </div>
            <div class="chart-badge hierarchical">Hierarchical</div>
          </div>
          <div class="chart-description">State → Airport → Delay Type</div>
          <SunburstChart 
            :filters="filters"
            @delay-type-selected="onDelayTypeSelected"
          />
        </div>
      </div>

      <!-- Parallel Coordinates -->
      <div class="chart-container full-width" :class="{ 'chart-filtered': filters.selectedCarrier }">
        <div class="chart-header">
          <div class="chart-title">
            <span>Airline Performance Comparison</span>
          </div>
          <div class="chart-badge multi-dimensional">Multi-dimensional</div>
        </div>
        <div class="chart-description">
          <span class="interaction-hint">💡 Hover to highlight airlines</span>
          <span class="interaction-hint">🖱️ Click to select/filter</span>
          <span class="interaction-hint">📏 Drag on axes to brush-filter</span>
        </div>
        <ParallelCoordinates 
          :filters="filters"
          @carrier-selected="onCarrierSelected"
        />
      </div>

      <!-- Stream Graph + Bubble Chart -->
      <div class="dashboard-row">
        <div class="chart-container" :class="{ 'chart-filtered': filters.selectedDelayType }">
          <div class="chart-header">
            <div class="chart-title">
              <span>Delay Trends Over Time</span>
            </div>
            <div class="chart-badge temporal">Temporal</div>
          </div>
          <div class="chart-description">Stacked delay types showing seasonal patterns • Click a layer to filter</div>
          <StreamGraph 
            :filters="filters"
            @delay-type-selected="onDelayTypeSelected"
          />
        </div>

        <div class="chart-container" :class="{ 'chart-filtered': filters.selectedAirport }">
          <div class="chart-header">
            <div class="chart-title">
              <span>Airport Performance Matrix</span>
            </div>
            <div class="chart-badge scatter">Scatter</div>
          </div>
          <div class="chart-description">
            <span class="encoding-hint">Size = Total Flights</span>
            <span class="encoding-hint">Color = Dominant Delay Type</span>
            <span class="encoding-hint">Y = Avg Delay</span>
          </div>
          <BubbleChart 
            :filters="filters"
            @airport-selected="onAirportSelected"
          />
        </div>
      </div>

      <!-- Insights Section -->
      <div class="insights-section" v-if="hasActiveFilters">
        <div class="insights-header">
          <span>Filtered Data Insights</span>
        </div>
        <div class="insights-content">
          <p v-if="filters.selectedState">
            Viewing airports and airlines operating in <strong>{{ getStateName(filters.selectedState) }}</strong>
          </p>
          <p v-if="filters.selectedCarrier">
            Filtering for <strong>{{ filters.selectedCarrier }}</strong> airline performance across all metrics
          </p>
          <p v-if="filters.selectedAirport">
            Highlighting <strong>{{ filters.selectedAirport }}</strong> airport data
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import ChoroplethMap from '../components/ChoroplethMap.vue'
import SunburstChart from '../components/SunburstChart.vue'
import ParallelCoordinates from '../components/ParallelCoordinates.vue'
import StreamGraph from '../components/StreamGraph.vue'
import BubbleChart from '../components/BubbleChart.vue'
import { stateNames } from '@/utils/chartUtils'

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
    // Global filter state - shared across all charts
    const filters = reactive({
      selectedState: null,
      selectedAirport: null,
      selectedCarrier: null,
      selectedDelayType: null,
      dateRange: null
    })

    const hasActiveFilters = computed(() => {
      return filters.selectedState || 
             filters.selectedAirport || 
             filters.selectedCarrier ||
             filters.selectedDelayType
    })

    const getStateName = (stateCode) => {
      return stateNames[stateCode] || stateCode
    }

    // Filter event handlers
    const onStateSelected = (state) => {
      filters.selectedState = state === filters.selectedState ? null : state
      // Clear airport filter when state changes (airports are state-specific)
      if (state !== filters.selectedState) {
        filters.selectedAirport = null
      }
      console.log('State filter:', filters.selectedState)
    }

    const onAirportSelected = (airport) => {
      filters.selectedAirport = airport === filters.selectedAirport ? null : airport
      console.log('Airport filter:', filters.selectedAirport)
    }

    const onCarrierSelected = (carrier) => {
      filters.selectedCarrier = carrier === filters.selectedCarrier ? null : carrier
      console.log('Carrier filter:', filters.selectedCarrier)
    }

    const onDelayTypeSelected = (delayType) => {
      filters.selectedDelayType = delayType === filters.selectedDelayType ? null : delayType
      console.log('Delay type filter:', filters.selectedDelayType)
    }

    const clearFilter = (filterType) => {
      switch(filterType) {
        case 'state':
          filters.selectedState = null
          filters.selectedAirport = null // Clear dependent filter
          break
        case 'airport':
          filters.selectedAirport = null
          break
        case 'carrier':
          filters.selectedCarrier = null
          break
        case 'delayType':
          filters.selectedDelayType = null
          break
      }
    }

    const resetFilters = () => {
      filters.selectedState = null
      filters.selectedAirport = null
      filters.selectedCarrier = null
      filters.selectedDelayType = null
      filters.dateRange = null
      console.log('All filters reset')
    }

    return {
      filters,
      hasActiveFilters,
      getStateName,
      onStateSelected,
      onAirportSelected,
      onCarrierSelected,
      onDelayTypeSelected,
      clearFilter,
      resetFilters
    }
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: var(--bg-dark);
}

.header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 25px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
}

.header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.header-subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.header-controls {
  display: flex;
  gap: 15px;
}

.header-controls .btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 20px 30px;
}

/* Filter Banner Styles */
.filter-banner {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
  border-left: 4px solid var(--primary);
  padding: 15px 20px;
  margin-bottom: 25px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid rgba(102, 126, 234, 0.25);
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
  font-weight: 600;
  color: var(--text-secondary);
}

.filter-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tag:hover {
  transform: translateY(-1px);
}

.tag-close {
  font-size: 1rem;
  font-weight: bold;
  opacity: 0.7;
  margin-left: 4px;
}

.filter-tag:hover .tag-close {
  opacity: 1;
}

.state-tag {
  background: rgba(39, 174, 96, 0.2);
  color: #27ae60;
  border: 1px solid rgba(39, 174, 96, 0.3);
}

.airport-tag {
  background: rgba(52, 152, 219, 0.2);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.3);
}

.carrier-tag {
  background: rgba(155, 89, 182, 0.2);
  color: #9b59b6;
  border: 1px solid rgba(155, 89, 182, 0.3);
}

.delay-tag {
  background: rgba(243, 156, 18, 0.2);
  color: #f39c12;
  border: 1px solid rgba(243, 156, 18, 0.3);
}

.filter-clear {
  color: var(--danger);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  padding: 8px 16px;
  border-radius: 8px;
  transition: var(--transition);
  white-space: nowrap;
}

.filter-clear:hover {
  background: rgba(229, 62, 62, 0.15);
}

/* Slide fade transition */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 15px;
  margin-bottom: 15px;
}

.dashboard-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 15px;
}

.full-width {
  margin-bottom: 15px;
}

/* Chart Container Styles */
.chart-container {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
  position: relative;
}

.chart-container:hover {
  box-shadow: var(--shadow-md);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

.chart-container.chart-filtered {
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.15);
}

.chart-container.chart-filtered::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--primary-dark));
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chart-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-title .icon {
  font-size: 1.4rem;
}

.chart-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chart-badge.geographic {
  background: rgba(39, 174, 96, 0.15);
  color: #27ae60;
}

.chart-badge.hierarchical {
  background: rgba(243, 156, 18, 0.15);
  color: #f39c12;
}

.chart-badge.multi-dimensional {
  background: rgba(155, 89, 182, 0.15);
  color: #9b59b6;
}

.chart-badge.temporal {
  background: rgba(52, 152, 219, 0.15);
  color: #3498db;
}

.chart-badge.scatter {
  background: rgba(231, 76, 60, 0.15);
  color: #e74c3c;
}

.chart-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.interaction-hint,
.encoding-hint {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  font-size: 0.8rem;
}

/* Insights Section */
.insights-section {
  margin-top: 30px;
  padding: 20px 25px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.insights-header {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.insights-content {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
}

.insights-content p {
  margin-bottom: 8px;
}

.insights-content strong {
  color: var(--text-primary);
}

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-grid,
  .dashboard-row {
    grid-template-columns: 1fr;
  }
  
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .filter-banner {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .filter-info {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 15px;
  }
  
  .chart-container {
    padding: 15px;
  }
  
  .chart-description {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
