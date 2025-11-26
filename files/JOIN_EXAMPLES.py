"""
PRACTICAL JOIN EXAMPLES
=======================
Python/Pandas code showing how to connect the datasets

Usage:
    Copy-paste these examples into your merge script
"""

import pandas as pd
import numpy as np

# ============================================================================
# LOAD ALL DATASETS
# ============================================================================

# Load data
bts = pd.read_csv('data/raw/bts_airline_delays.csv')
airports = pd.read_csv('data/raw/airports_geographic.csv')
weather = pd.read_csv('data/raw/weather_all_airports.csv')
reviews = pd.read_csv('data/raw/skytrax_airline_reviews.csv')

print("Datasets loaded!")
print(f"BTS: {len(bts):,} rows")
print(f"Airports: {len(airports):,} rows")
print(f"Weather: {len(weather):,} rows")
print(f"Reviews: {len(reviews):,} rows")

# ============================================================================
# JOIN 1: BTS + AIRPORTS (Add Geographic Data)
# ============================================================================

print("\n" + "="*70)
print("JOIN 1: BTS + AIRPORTS")
print("="*70)

# Clean airport codes (remove whitespace, uppercase)
bts['Origin'] = bts['Origin'].str.strip().str.upper()
airports['iata_code'] = airports['iata_code'].str.strip().str.upper()

# Filter to US airports only (optional but recommended)
us_airports = airports[airports['iso_country'] == 'US'].copy()

# Perform LEFT JOIN (keep all BTS records)
bts_with_geo = bts.merge(
    us_airports[['iata_code', 'name', 'latitude_deg', 'longitude_deg', 'elevation_ft', 'type']],
    left_on='Origin',
    right_on='iata_code',
    how='left'
)

# Rename columns for clarity
bts_with_geo = bts_with_geo.rename(columns={
    'name': 'origin_airport_name',
    'latitude_deg': 'origin_lat',
    'longitude_deg': 'origin_lon',
    'elevation_ft': 'origin_elevation',
    'type': 'origin_type'
})

print(f"✓ Merged BTS + Airports: {len(bts_with_geo):,} rows")
print(f"  Matched airports: {bts_with_geo['origin_lat'].notna().sum():,}")
print(f"  Unmatched: {bts_with_geo['origin_lat'].isna().sum():,}")

# Example: Show first few rows
print("\nSample joined data:")
print(bts_with_geo[['Origin', 'origin_airport_name', 'origin_lat', 'origin_lon', 'origin_elevation']].head())

# ============================================================================
# JOIN 2: BTS + WEATHER (Add Weather Conditions)
# ============================================================================

print("\n" + "="*70)
print("JOIN 2: BTS + WEATHER")
print("="*70)

# Convert dates to datetime
bts_with_geo['FlightDate'] = pd.to_datetime(bts_with_geo['FlightDate'])
weather['valid'] = pd.to_datetime(weather['valid'])

# Extract date only (ignore time for daily matching)
bts_with_geo['date_only'] = bts_with_geo['FlightDate'].dt.date
weather['date_only'] = weather['valid'].dt.date

# OPTION A: Match with daily average weather
# Aggregate weather to daily averages
weather_daily = weather.groupby(['station', 'date_only']).agg({
    'tmpf': 'mean',      # Average temperature
    'dwpf': 'mean',      # Average dew point
    'relh': 'mean',      # Average humidity
    'sknt': 'mean',      # Average wind speed
    'p01i': 'sum',       # Total precipitation
    'vsby': 'mean',      # Average visibility
    'gust': 'max'        # Max gust
}).reset_index()

print(f"  Weather aggregated to {len(weather_daily):,} daily records")

# Merge
bts_with_weather = bts_with_geo.merge(
    weather_daily,
    left_on=['Origin', 'date_only'],
    right_on=['station', 'date_only'],
    how='left'
)

print(f"✓ Merged BTS + Weather: {len(bts_with_weather):,} rows")
print(f"  Weather matched: {bts_with_weather['tmpf'].notna().sum():,}")
print(f"  No weather data: {bts_with_weather['tmpf'].isna().sum():,}")

# Example: Show correlation
print("\nWeather Correlation with Delays:")
if bts_with_weather['vsby'].notna().sum() > 0:
    corr = bts_with_weather[['vsby', 'WeatherDelay']].corr().iloc[0, 1]
    print(f"  Visibility vs Weather Delay correlation: {corr:.3f}")

# ============================================================================
# JOIN 3: BTS + REVIEWS (Add Customer Sentiment)
# ============================================================================

print("\n" + "="*70)
print("JOIN 3: BTS + REVIEWS")
print("="*70)

# Create airline mapping (from airline names to carrier codes)
airline_mapping = {
    'american-airlines': 'AA',
    'delta-air-lines': 'DL',
    'united-airlines': 'UA',
    'southwest-airlines': 'WN',
    'alaska-airlines': 'AS',
    'jetblue-airways': 'B6',
    'spirit-airlines': 'NK',
    'frontier-airlines': 'F9',
    'allegiant-air': 'G4',
    'hawaiian-airlines': 'HA',
}

# Apply mapping
reviews['carrier_code'] = reviews['airline_name'].map(airline_mapping)

# Parse dates
reviews['date_flown'] = pd.to_datetime(reviews['date_flown'], errors='coerce')
reviews['year_month'] = reviews['date_flown'].dt.to_period('M')

# Add year_month to BTS
bts_with_weather['year_month'] = bts_with_weather['FlightDate'].dt.to_period('M')

# Aggregate reviews by carrier and month
review_summary = reviews[reviews['carrier_code'].notna()].groupby(['carrier_code', 'year_month']).agg({
    'overall_rating': 'mean',
    'recommended': lambda x: (x == 1).sum(),  # Count recommendations
    'content': 'count'  # Count total reviews
}).reset_index()

review_summary.columns = ['carrier_code', 'year_month', 'avg_rating', 'num_recommended', 'num_reviews']

print(f"  Reviews aggregated to {len(review_summary):,} carrier-month combinations")

# Merge
bts_complete = bts_with_weather.merge(
    review_summary,
    left_on=['Carrier', 'year_month'],
    right_on=['carrier_code', 'year_month'],
    how='left'
)

print(f"✓ Merged BTS + Reviews: {len(bts_complete):,} rows")
print(f"  Review data matched: {bts_complete['avg_rating'].notna().sum():,}")

# ============================================================================
# CREATE VISUALIZATION-READY DATASETS
# ============================================================================

print("\n" + "="*70)
print("CREATING VISUALIZATION DATASETS")
print("="*70)

# Dataset 1: Airport Summary (for map and bar chart)
airport_summary = bts_complete.groupby('Origin').agg({
    'DepDelay': 'mean',
    'CarrierDelay': 'mean',
    'WeatherDelay': 'mean',
    'NASDelay': 'mean',
    'SecurityDelay': 'mean',
    'LateAircraftDelay': 'mean',
    'origin_lat': 'first',
    'origin_lon': 'first',
    'origin_elevation': 'first',
    'origin_airport_name': 'first'
}).reset_index()

print(f"✓ Airport summary: {len(airport_summary)} airports")

# Dataset 2: Weather-Delay correlation (for scatter plot)
weather_delay_corr = bts_complete[
    (bts_complete['vsby'].notna()) & 
    (bts_complete['WeatherDelay'].notna()) &
    (bts_complete['WeatherDelay'] > 0)
][['Origin', 'FlightDate', 'vsby', 'tmpf', 'p01i', 'WeatherDelay']].copy()

print(f"✓ Weather-delay data: {len(weather_delay_corr):,} observations")

# Dataset 3: Carrier sentiment vs performance (for gap analysis)
carrier_summary = bts_complete.groupby('Carrier').agg({
    'DepDelay': 'mean',
    'WeatherDelay': 'mean',
    'CarrierDelay': 'mean',
    'avg_rating': 'mean',
    'num_reviews': 'sum'
}).reset_index()

carrier_summary = carrier_summary[carrier_summary['avg_rating'].notna()]

print(f"✓ Carrier summary: {len(carrier_summary)} airlines")

# Dataset 4: Time series (for trend analysis)
daily_summary = bts_complete.groupby('FlightDate').agg({
    'DepDelay': 'mean',
    'WeatherDelay': 'mean',
    'CarrierDelay': 'mean',
    'tmpf': 'mean',
    'p01i': 'mean'
}).reset_index()

print(f"✓ Daily time series: {len(daily_summary)} days")

# ============================================================================
# SAVE PROCESSED DATA
# ============================================================================

print("\n" + "="*70)
print("SAVING DATASETS")
print("="*70)

import os
os.makedirs('data/processed', exist_ok=True)

# Save complete merged dataset
bts_complete.to_csv('data/processed/merged_complete.csv', index=False)
print("✓ Saved: merged_complete.csv")

# Save visualization-ready datasets
airport_summary.to_csv('data/processed/viz_airport_summary.csv', index=False)
print("✓ Saved: viz_airport_summary.csv")

weather_delay_corr.to_csv('data/processed/viz_weather_delay.csv', index=False)
print("✓ Saved: viz_weather_delay.csv")

carrier_summary.to_csv('data/processed/viz_carrier_summary.csv', index=False)
print("✓ Saved: viz_carrier_summary.csv")

daily_summary.to_csv('data/processed/viz_daily_summary.csv', index=False)
print("✓ Saved: viz_daily_summary.csv")

# ============================================================================
# PRINT SUMMARY STATISTICS
# ============================================================================

print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)

print("\nTop 5 Airports by Average Delay:")
print(airport_summary.nlargest(5, 'DepDelay')[['Origin', 'origin_airport_name', 'DepDelay']])

print("\nTop 5 Airports by Weather Delay:")
print(airport_summary.nlargest(5, 'WeatherDelay')[['Origin', 'origin_airport_name', 'WeatherDelay']])

print("\nCarrier Ratings vs Delays:")
print(carrier_summary[['Carrier', 'DepDelay', 'avg_rating']].sort_values('avg_rating', ascending=False))

print("\nWeather Correlation:")
if len(weather_delay_corr) > 0:
    print(f"Average visibility: {weather_delay_corr['vsby'].mean():.1f} miles")
    print(f"Average weather delay: {weather_delay_corr['WeatherDelay'].mean():.1f} minutes")
    
    # Threshold analysis
    low_vis = weather_delay_corr[weather_delay_corr['vsby'] < 3]
    high_vis = weather_delay_corr[weather_delay_corr['vsby'] >= 3]
    
    if len(low_vis) > 0 and len(high_vis) > 0:
        print(f"\nVisibility Threshold Analysis:")
        print(f"  Avg delay when vsby < 3 miles: {low_vis['WeatherDelay'].mean():.1f} min")
        print(f"  Avg delay when vsby >= 3 miles: {high_vis['WeatherDelay'].mean():.1f} min")
        print(f"  Difference: {low_vis['WeatherDelay'].mean() - high_vis['WeatherDelay'].mean():.1f} min")

print("\n" + "="*70)
print("✅ ALL JOINS COMPLETE!")
print("="*70)
print("\nFiles ready for visualization:")
print("  • viz_airport_summary.csv    → For map and bar chart")
print("  • viz_weather_delay.csv      → For scatter plot")
print("  • viz_carrier_summary.csv    → For sentiment analysis")
print("  • viz_daily_summary.csv      → For time series")
print("\nNext step: Load these in your D3/Vue dashboard!")
print("="*70)

# ============================================================================
# EXAMPLE QUERIES FOR SPECIFIC VISUALIZATIONS
# ============================================================================

"""
EXAMPLE 1: Get data for geographic map
───────────────────────────────────────────────────────────────────────

df = pd.read_csv('data/processed/viz_airport_summary.csv')

# For D3 map visualization
map_data = df[['Origin', 'origin_lat', 'origin_lon', 'DepDelay']].to_dict('records')


EXAMPLE 2: Get data for stacked bar chart
───────────────────────────────────────────────────────────────────────

df = pd.read_csv('data/processed/viz_airport_summary.csv')

# Top 10 airports by total delay
top10 = df.nlargest(10, 'DepDelay')

# For stacked bar chart
bar_data = top10[[
    'Origin', 
    'CarrierDelay', 
    'WeatherDelay', 
    'NASDelay', 
    'LateAircraftDelay'
]].to_dict('records')


EXAMPLE 3: Get data for weather scatter plot
───────────────────────────────────────────────────────────────────────

df = pd.read_csv('data/processed/viz_weather_delay.csv')

# Sample if too many points
if len(df) > 5000:
    df = df.sample(5000)

scatter_data = df[['vsby', 'WeatherDelay', 'p01i']].to_dict('records')


EXAMPLE 4: Get data for sentiment gap analysis
───────────────────────────────────────────────────────────────────────

df = pd.read_csv('data/processed/viz_carrier_summary.csv')

gap_data = df[['Carrier', 'DepDelay', 'avg_rating']].to_dict('records')
"""
