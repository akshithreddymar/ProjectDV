"""
Airport Delay Analysis - Data Preprocessing & EDA
===================================================
This script processes BTS delay data, airport geographic data, and Skytrax reviews
to generate cleaned datasets for D3.js visualizations.

Output files:
1. state_summary.json - State-level aggregates for choropleth map
2. sunburst_data.json - Hierarchical delay breakdown for sunburst chart
3. carrier_metrics.csv - Multi-dimensional carrier comparison for parallel coordinates
4. temporal_delays.csv - Time series data for stream graph
5. airport_performance.csv - Airport metrics for bubble chart
6. reviews_processed.csv - Processed reviews with sentiment scores
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("AIRPORT DELAY ANALYSIS - DATA PREPROCESSING")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD DATASETS
# ============================================================================
print("\n[1/8] Loading datasets...")

# Load BTS delay data
print("  • Loading BTS delay data...")
# Adjust this path to where your BTS data is stored
bts_data = pd.read_csv('/Users/preddy/Desktop/DataVisualization/DV_PROJECT/public/Airline_Delay_Cause.csv')
print(f"    Loaded {len(bts_data):,} delay records")

# Load geographical data
print("  • Loading airport geographic data...")
geo_data = pd.read_csv('/Users/preddy/Desktop/DataVisualization/DV_PROJECT/public/airports_geographic.csv')
print(f"    Loaded {len(geo_data):,} airport records")

# Load reviews data
print("  • Loading Skytrax reviews...")
reviews_data = pd.read_csv('/Users/preddy/Desktop/DataVisualization/DV_PROJECT/public/skytrax_airline_reviews.csv')
print(f"    Loaded {len(reviews_data):,} reviews")

# ============================================================================
# STEP 2: DATA QUALITY CHECK
# ============================================================================
print("\n[2/8] Data Quality Assessment...")

print("\n  BTS Delay Data:")
print(f"    Date Range: {bts_data['year'].min()}-{bts_data['year'].max()}")
print(f"    Unique Airports: {bts_data['airport'].nunique()}")
print(f"    Unique Carriers: {bts_data['carrier'].nunique()}")
print(f"    Missing Values: {bts_data.isnull().sum().sum()}")

print("\n  Geographic Data:")
print(f"    Total Airports: {len(geo_data)}")
print(f"    US Airports: {len(geo_data[geo_data['iso_country'] == 'US'])}")
print(f"    With IATA codes: {geo_data['iata_code'].notna().sum()}")

print("\n  Reviews Data:")
print(f"    Date Range: {reviews_data['date'].min()} to {reviews_data['date'].max()}")
print(f"    Unique Airlines: {reviews_data['airline_name'].nunique()}")
print(f"    Reviews with ratings: {reviews_data['overall_rating'].notna().sum()}")

# ============================================================================
# STEP 3: CREATE AIRPORT-TO-STATE MAPPING
# ============================================================================
print("\n[3/8] Creating airport-to-state mapping...")

# Extract state codes from iso_region (format: US-XX)
geo_data['state'] = geo_data['iso_region'].str.replace('US-', '')

# Create mapping dictionary: airport code -> state
airport_to_state = geo_data[geo_data['iata_code'].notna()].set_index('iata_code')['state'].to_dict()

# Also create full info mapping
airport_info = geo_data[geo_data['iata_code'].notna()].set_index('iata_code')[
    ['name', 'latitude_deg', 'longitude_deg', 'state', 'municipality']
].to_dict('index')

print(f"    Mapped {len(airport_to_state)} airports to states")

# Add state to BTS data
bts_data['state'] = bts_data['airport'].map(airport_to_state)
print(f"    {bts_data['state'].notna().sum()} BTS records have state mappings")

# ============================================================================
# STEP 4: CARRIER NAME MAPPING
# ============================================================================
print("\n[4/8] Creating carrier name mappings...")

# Common US carriers in BTS data
carrier_mapping = {
    'AA': 'American Airlines',
    'AS': 'Alaska Airlines',
    'B6': 'JetBlue Airways',
    'DL': 'Delta Air Lines',
    'F9': 'Frontier Airlines',
    'G4': 'Allegiant Air',
    'HA': 'Hawaiian Airlines',
    'NK': 'Spirit Airlines',
    'UA': 'United Airlines',
    'WN': 'Southwest Airlines',
    'YV': 'Mesa Airlines',
    'YX': 'Republic Airline',
    'G7': 'GoJet Airlines',
}

# Add full carrier names to BTS data
bts_data['carrier_full_name'] = bts_data['carrier'].map(carrier_mapping).fillna(bts_data['carrier_name'])

# Normalize review airline names for matching
reviews_data['airline_normalized'] = reviews_data['airline_name'].str.lower().str.replace('-', ' ')

print(f"    Mapped {len(carrier_mapping)} carriers")

# ============================================================================
# STEP 5: CALCULATE DERIVED METRICS
# ============================================================================
print("\n[5/8] Calculating derived metrics...")

# Calculate delay rates and percentages
bts_data['delay_rate'] = (bts_data['arr_del15'] / bts_data['arr_flights'] * 100).fillna(0)
bts_data['cancel_rate'] = (bts_data['arr_cancelled'] / bts_data['arr_flights'] * 100).fillna(0)
bts_data['ontime_rate'] = 100 - bts_data['delay_rate']

# Calculate average delay per flight
bts_data['avg_delay_per_flight'] = (bts_data['arr_delay'] / bts_data['arr_flights']).fillna(0)

# Calculate delay composition percentages
total_delay = (bts_data['carrier_delay'] + bts_data['weather_delay'] + 
               bts_data['nas_delay'] + bts_data['security_delay'] + 
               bts_data['late_aircraft_delay'])

bts_data['carrier_delay_pct'] = (bts_data['carrier_delay'] / total_delay * 100).fillna(0)
bts_data['weather_delay_pct'] = (bts_data['weather_delay'] / total_delay * 100).fillna(0)
bts_data['nas_delay_pct'] = (bts_data['nas_delay'] / total_delay * 100).fillna(0)
bts_data['security_delay_pct'] = (bts_data['security_delay'] / total_delay * 100).fillna(0)
bts_data['late_aircraft_delay_pct'] = (bts_data['late_aircraft_delay'] / total_delay * 100).fillna(0)

# Determine dominant delay type
delay_cols = ['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
bts_data['dominant_delay_type'] = bts_data[delay_cols].idxmax(axis=1).str.replace('_delay', '')

print("    ✓ Delay rates calculated")
print("    ✓ Delay composition analyzed")

# ============================================================================
# STEP 6: GENERATE AGGREGATED DATASETS
# ============================================================================
print("\n[6/8] Generating aggregated datasets...")

# -------------------------
# 6.1: STATE SUMMARY (for Choropleth Map)
# -------------------------
print("\n  6.1: State-level summary...")

state_summary = bts_data.groupby('state').agg({
    'arr_flights': 'sum',
    'arr_del15': 'sum',
    'arr_delay': 'sum',
    'arr_cancelled': 'sum',
    'carrier_delay': 'sum',
    'weather_delay': 'sum',
    'nas_delay': 'sum',
    'security_delay': 'sum',
    'late_aircraft_delay': 'sum'
}).reset_index()

state_summary['avg_delay'] = state_summary['arr_delay'] / state_summary['arr_flights']
state_summary['delay_rate'] = (state_summary['arr_del15'] / state_summary['arr_flights'] * 100)
state_summary['cancel_rate'] = (state_summary['arr_cancelled'] / state_summary['arr_flights'] * 100)

# Find worst airport per state
worst_airport_per_state = bts_data.groupby(['state', 'airport']).agg({
    'avg_delay_per_flight': 'mean'
}).reset_index()
worst_airport_per_state = worst_airport_per_state.loc[
    worst_airport_per_state.groupby('state')['avg_delay_per_flight'].idxmax()
]

state_summary = state_summary.merge(
    worst_airport_per_state[['state', 'airport']].rename(columns={'airport': 'worst_airport'}),
    on='state',
    how='left'
)

# Convert to dictionary for JSON
state_dict = {}
for _, row in state_summary.iterrows():
    if pd.notna(row['state']):
        state_dict[row['state']] = {
            'total_flights': int(row['arr_flights']),
            'avg_delay': round(float(row['avg_delay']), 2),
            'delay_rate': round(float(row['delay_rate']), 2),
            'cancel_rate': round(float(row['cancel_rate']), 2),
            'worst_airport': str(row['worst_airport']) if pd.notna(row['worst_airport']) else None,
            'total_delays': int(row['arr_del15'])
        }

with open('/mnt/user-data/outputs/state_summary.json', 'w') as f:
    json.dump(state_dict, f, indent=2)

print(f"    ✓ Created state_summary.json ({len(state_dict)} states)")

# -------------------------
# 6.2: SUNBURST DATA (Hierarchical)
# -------------------------
print("\n  6.2: Sunburst hierarchical data...")

def create_sunburst_node(name, value, children=None):
    node = {"name": name, "value": value}
    if children:
        node["children"] = children
    return node

# Group by state and airport, then by delay type
sunburst_data = []

for state in bts_data['state'].dropna().unique():
    state_data = bts_data[bts_data['state'] == state]
    
    # Get airports in this state
    airport_children = []
    for airport in state_data['airport'].unique():
        airport_data = state_data[state_data['airport'] == airport]
        
        # Calculate delay type breakdown for this airport
        delay_types = []
        total_carrier = airport_data['carrier_delay'].sum()
        total_weather = airport_data['weather_delay'].sum()
        total_nas = airport_data['nas_delay'].sum()
        total_security = airport_data['security_delay'].sum()
        total_late = airport_data['late_aircraft_delay'].sum()
        
        if total_carrier > 0:
            delay_types.append(create_sunburst_node("Carrier", int(total_carrier)))
        if total_weather > 0:
            delay_types.append(create_sunburst_node("Weather", int(total_weather)))
        if total_nas > 0:
            delay_types.append(create_sunburst_node("NAS", int(total_nas)))
        if total_security > 0:
            delay_types.append(create_sunburst_node("Security", int(total_security)))
        if total_late > 0:
            delay_types.append(create_sunburst_node("Late Aircraft", int(total_late)))
        
        if delay_types:
            airport_node = create_sunburst_node(
                airport,
                int(airport_data['arr_delay'].sum()),
                delay_types
            )
            airport_children.append(airport_node)
    
    if airport_children:
        state_node = create_sunburst_node(
            state,
            int(state_data['arr_delay'].sum()),
            airport_children
        )
        sunburst_data.append(state_node)

sunburst_root = create_sunburst_node("USA", 0, sunburst_data)

with open('/mnt/user-data/outputs/sunburst_data.json', 'w') as f:
    json.dump(sunburst_root, f, indent=2)

print(f"    ✓ Created sunburst_data.json")

# -------------------------
# 6.3: CARRIER METRICS (for Parallel Coordinates)
# -------------------------
print("\n  6.3: Carrier comparison metrics...")

carrier_metrics = bts_data.groupby('carrier_full_name').agg({
    'arr_flights': 'sum',
    'arr_delay': 'sum',
    'arr_cancelled': 'sum',
    'arr_del15': 'sum',
    'carrier_delay': 'sum',
    'weather_delay': 'sum',
    'nas_delay': 'sum',
    'late_aircraft_delay': 'sum'
}).reset_index()

carrier_metrics['avg_delay'] = carrier_metrics['arr_delay'] / carrier_metrics['arr_flights']
carrier_metrics['cancel_rate'] = (carrier_metrics['arr_cancelled'] / carrier_metrics['arr_flights'] * 100)
carrier_metrics['ontime_rate'] = 100 - ((carrier_metrics['arr_del15'] / carrier_metrics['arr_flights']) * 100)

# Calculate delay composition percentages
total_delay_carrier = (carrier_metrics['carrier_delay'] + carrier_metrics['weather_delay'] + 
                       carrier_metrics['nas_delay'] + carrier_metrics['late_aircraft_delay'])

carrier_metrics['carrier_delay_pct'] = (carrier_metrics['carrier_delay'] / total_delay_carrier * 100).fillna(0)
carrier_metrics['weather_delay_pct'] = (carrier_metrics['weather_delay'] / total_delay_carrier * 100).fillna(0)
carrier_metrics['nas_delay_pct'] = (carrier_metrics['nas_delay'] / total_delay_carrier * 100).fillna(0)

# Add review ratings (we'll calculate this in step 7)
carrier_metrics['avg_rating'] = 0  # Placeholder

# Select columns for output
carrier_output = carrier_metrics[[
    'carrier_full_name', 'arr_flights', 'avg_delay', 'cancel_rate',
    'weather_delay_pct', 'carrier_delay_pct', 'nas_delay_pct', 'ontime_rate'
]].copy()

carrier_output.columns = [
    'carrier', 'total_flights', 'avg_delay_min', 'cancel_rate_pct',
    'weather_pct', 'carrier_pct', 'nas_pct', 'ontime_pct'
]

carrier_output.to_csv('/mnt/user-data/outputs/carrier_metrics.csv', index=False)
print(f"    ✓ Created carrier_metrics.csv ({len(carrier_output)} carriers)")

# -------------------------
# 6.4: TEMPORAL DELAYS (for Stream Graph)
# -------------------------
print("\n  6.4: Temporal delay patterns...")

# Create year-month column
bts_data['year_month'] = bts_data['year'].astype(str) + '-' + bts_data['month'].astype(str).str.zfill(2)

temporal_delays = bts_data.groupby('year_month').agg({
    'carrier_delay': 'sum',
    'weather_delay': 'sum',
    'nas_delay': 'sum',
    'security_delay': 'sum',
    'late_aircraft_delay': 'sum',
    'arr_flights': 'sum'
}).reset_index()

temporal_delays = temporal_delays.sort_values('year_month')

temporal_delays.to_csv('/mnt/user-data/outputs/temporal_delays.csv', index=False)
print(f"    ✓ Created temporal_delays.csv ({len(temporal_delays)} time periods)")

# -------------------------
# 6.5: AIRPORT PERFORMANCE (for Bubble Chart)
# -------------------------
print("\n  6.5: Airport performance metrics...")

airport_performance = bts_data.groupby('airport').agg({
    'arr_flights': 'sum',
    'arr_delay': 'sum',
    'arr_cancelled': 'sum',
    'state': 'first',
    'dominant_delay_type': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'unknown'
}).reset_index()

airport_performance['avg_delay'] = airport_performance['arr_delay'] / airport_performance['arr_flights']

# Add airport names and coordinates
airport_performance['airport_name'] = airport_performance['airport'].map(
    lambda x: airport_info.get(x, {}).get('name', x) if x in airport_info else x
)
airport_performance['latitude'] = airport_performance['airport'].map(
    lambda x: airport_info.get(x, {}).get('latitude_deg', None) if x in airport_info else None
)
airport_performance['longitude'] = airport_performance['airport'].map(
    lambda x: airport_info.get(x, {}).get('longitude_deg', None) if x in airport_info else None
)

# Filter to airports with significant traffic (>1000 flights)
airport_performance = airport_performance[airport_performance['arr_flights'] > 1000]

airport_output = airport_performance[[
    'airport', 'airport_name', 'state', 'arr_flights', 'avg_delay',
    'arr_cancelled', 'dominant_delay_type', 'latitude', 'longitude'
]].copy()

airport_output.columns = [
    'airport_code', 'airport_name', 'state', 'total_flights', 'avg_delay_min',
    'total_cancelled', 'dominant_delay_type', 'latitude', 'longitude'
]

airport_output.to_csv('/mnt/user-data/outputs/airport_performance.csv', index=False)
print(f"    ✓ Created airport_performance.csv ({len(airport_output)} airports)")

# ============================================================================
# STEP 7: PROCESS REVIEWS (with Sentiment Analysis)
# ============================================================================
print("\n[7/8] Processing reviews...")

# Simple sentiment analysis based on ratings
def calculate_sentiment(row):
    """Calculate sentiment score from -1 (negative) to 1 (positive)"""
    if pd.isna(row['overall_rating']):
        return 0
    
    # Normalize rating (1-10) to sentiment (-1 to 1)
    # Rating 1-5 = negative, 6-8 = neutral/positive, 9-10 = very positive
    rating = float(row['overall_rating'])
    if rating <= 5:
        return (rating - 5) / 5  # Maps 1->-0.8, 5->0
    else:
        return (rating - 5) / 5  # Maps 6->0.2, 10->1

reviews_data['sentiment_score'] = reviews_data.apply(calculate_sentiment, axis=1)

# Check if review mentions delays
reviews_data['mentions_delay'] = reviews_data['content'].fillna('').str.lower().str.contains(
    'delay|late|wait|held|stuck|cancel', regex=True
)

# Extract US airline reviews only
us_airlines = list(carrier_mapping.values())
us_reviews = reviews_data[reviews_data['airline_name'].isin([
    'alaska-airlines', 'allegiant-air', 'american-airlines', 'delta-air-lines',
    'frontier-airlines', 'hawaiian-airlines', 'jetblue-airways', 'southwest-airlines',
    'spirit-airlines', 'united-airlines'
])]

print(f"    Found {len(us_reviews)} US airline reviews")
print(f"    {us_reviews['mentions_delay'].sum()} mention delays")

# Aggregate by airline
review_summary = us_reviews.groupby('airline_name').agg({
    'overall_rating': 'mean',
    'sentiment_score': 'mean',
    'mentions_delay': 'sum',
    'recommended': lambda x: (x == '1').sum() / len(x) * 100
}).reset_index()

review_summary.columns = ['airline', 'avg_rating', 'avg_sentiment', 'delay_mentions', 'recommend_pct']

review_summary.to_csv('/mnt/user-data/outputs/reviews_summary.csv', index=False)
print(f"    ✓ Created reviews_summary.csv")

# ============================================================================
# STEP 8: GENERATE SUMMARY STATISTICS
# ============================================================================
print("\n[8/8] Generating summary statistics...")

summary_stats = {
    "dataset_overview": {
        "bts_records": len(bts_data),
        "airports": bts_data['airport'].nunique(),
        "carriers": bts_data['carrier'].nunique(),
        "states": bts_data['state'].nunique(),
        "years": f"{bts_data['year'].min()}-{bts_data['year'].max()}",
        "total_flights": int(bts_data['arr_flights'].sum()),
        "total_delays": int(bts_data['arr_del15'].sum()),
        "total_cancellations": int(bts_data['arr_cancelled'].sum())
    },
    "top_delay_causes": {
        "weather": int(bts_data['weather_delay'].sum()),
        "carrier": int(bts_data['carrier_delay'].sum()),
        "nas": int(bts_data['nas_delay'].sum()),
        "late_aircraft": int(bts_data['late_aircraft_delay'].sum()),
        "security": int(bts_data['security_delay'].sum())
    },
    "worst_airports": bts_data.groupby('airport').agg({
        'avg_delay_per_flight': 'mean'
    }).nlargest(10, 'avg_delay_per_flight').to_dict()['avg_delay_per_flight'],
    "best_carriers": carrier_metrics.nsmallest(5, 'avg_delay')[['carrier_full_name', 'avg_delay']].to_dict('records')
}

with open('/mnt/user-data/outputs/summary_stats.json', 'w') as f:
    json.dump(summary_stats, f, indent=2)

print("\n" + "=" * 80)
print("✓ DATA PREPROCESSING COMPLETE!")
print("=" * 80)
print("\nGenerated files in /outputs:")
print("  1. state_summary.json - State-level aggregates")
print("  2. sunburst_data.json - Hierarchical delay breakdown")
print("  3. carrier_metrics.csv - Carrier comparison metrics")
print("  4. temporal_delays.csv - Time series data")
print("  5. airport_performance.csv - Airport metrics")
print("  6. reviews_summary.csv - Review analysis")
print("  7. summary_stats.json - Overall statistics")
print("\nReady for D3.js visualization!")
print("=" * 80)




