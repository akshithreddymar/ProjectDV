"""
Automatic Dataset Downloader
=============================
Downloads all datasets for Airline Performance Dashboard project

This script will:
1. Create data/raw/ folder structure
2. Download all 4 datasets automatically
3. Show progress and file sizes
4. Verify downloads

Usage:
    python download_all_datasets.py
"""

import urllib.request
import os
import time
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Dataset URLs
DATASETS = {
    'airports': {
        'url': 'https://davidmegginson.github.io/ourairports-data/airports.csv',
        'filename': 'airports_geographic.csv',
        'description': 'Airport Geographic Data'
    },
    'reviews': {
        'url': 'https://raw.githubusercontent.com/quankiquanki/skytrax-reviews-dataset/master/data/airline.csv',
        'filename': 'skytrax_airline_reviews.csv',
        'description': 'Skytrax Airline Reviews'
    },
    'weather': {
        'url': 'https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=ATL&station=ORD&station=DEN&station=LAX&station=JFK&station=DFW&station=SFO&station=MIA&data=tmpf&data=dwpf&data=relh&data=drct&data=sknt&data=p01i&data=vsby&data=gust&data=skyc1&data=skyc2&data=feel&year1=2023&month1=1&day1=1&year2=2024&month2=12&day2=31&tz=Etc/UTC&format=comma&latlon=yes',
        'filename': 'weather_all_airports.csv',
        'description': 'Weather Data (8 Airports Combined)'
    }
}

# Output directory
OUTPUT_DIR = '/Users/preddy/Desktop/DataVisualization/InClass_Activity/DV_PROJECT/data'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_directory():
    """Create the output directory if it doesn't exist."""
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {OUTPUT_DIR}")

def format_size(bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def download_with_progress(url, output_path, description):
    """
    Download a file with progress indication.
    """
    print(f"\n{'='*70}")
    print(f"📥 Downloading: {description}")
    print(f"{'='*70}")
    print(f"URL: {url[:80]}...")
    print(f"Saving to: {output_path}")
    print()
    
    try:
        # Download with progress
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                
                # Progress bar
                bar_length = 40
                filled = int(bar_length * percent / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                print(f'\r  [{bar}] {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)', 
                      end='', flush=True)
            else:
                # Unknown size
                downloaded_mb = downloaded / (1024 * 1024)
                print(f'\r  Downloaded: {downloaded_mb:.1f} MB', end='', flush=True)
        
        # Perform download
        urllib.request.urlretrieve(url, output_path, reporthook)
        print()  # New line after progress
        
        # Get final file size
        file_size = os.path.getsize(output_path)
        print(f"✓ Download complete! Size: {format_size(file_size)}")
        
        return True, file_size
        
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        return False, 0

def verify_file(filepath, min_size_kb=10):
    """
    Verify that a file exists and is not empty/corrupted.
    """
    if not os.path.exists(filepath):
        return False, "File does not exist"
    
    file_size = os.path.getsize(filepath)
    if file_size < min_size_kb * 1024:
        return False, f"File too small ({format_size(file_size)}), may be corrupted"
    
    return True, f"OK ({format_size(file_size)})"

# ============================================================================
# MAIN DOWNLOAD FUNCTION
# ============================================================================

def main():
    """
    Main function to download all datasets.
    """
    print()
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "AUTOMATIC DATASET DOWNLOADER" + " "*25 + "║")
    print("╚" + "="*68 + "╝")
    print()
    print("This script will download 3 datasets:")
    print("  1. Airport Geographic Data (~5 MB)")
    print("  2. Skytrax Airline Reviews (~33 MB)")
    print("  3. Weather Data for 8 Airports (~15-25 MB)")
    print()
    print("Total estimated download: ~50-60 MB")
    print("Estimated time: 2-5 minutes (depends on internet speed)")
    print()
    
    input("Press ENTER to start downloading...")
    print()
    
    # Create output directory
    create_directory()
    print()
    
    # Track results
    results = {}
    total_size = 0
    start_time = time.time()
    
    # Download each dataset
    for key, dataset in DATASETS.items():
        url = dataset['url']
        filename = dataset['filename']
        description = dataset['description']
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Check if file already exists
        if os.path.exists(output_path):
            print(f"\n⚠️  File already exists: {filename}")
            response = input("    Overwrite? (y/n): ").lower()
            if response != 'y':
                print("    Skipped.")
                file_size = os.path.getsize(output_path)
                results[key] = {'success': True, 'size': file_size, 'skipped': True}
                total_size += file_size
                continue
        
        # Download
        success, file_size = download_with_progress(url, output_path, description)
        results[key] = {'success': success, 'size': file_size, 'skipped': False}
        
        if success:
            total_size += file_size
        
        # Be nice to servers - wait between downloads
        if key != list(DATASETS.keys())[-1]:  # If not the last one
            time.sleep(2)
    
    # Calculate total time
    elapsed_time = time.time() - start_time
    
    # Print summary
    print()
    print("╔" + "="*68 + "╗")
    print("║" + " "*25 + "DOWNLOAD SUMMARY" + " "*27 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    success_count = sum(1 for r in results.values() if r['success'])
    
    print(f"{'Dataset':<35} {'Status':<15} {'Size':<15}")
    print("-" * 70)
    
    for key, dataset in DATASETS.items():
        result = results[key]
        filename = dataset['filename']
        
        if result.get('skipped'):
            status = "⊙ Skipped"
        elif result['success']:
            status = "✓ Success"
        else:
            status = "✗ Failed"
        
        size = format_size(result['size']) if result['size'] > 0 else "-"
        print(f"{filename:<35} {status:<15} {size:<15}")
    
    print("-" * 70)
    print(f"{'TOTAL':<35} {success_count}/{len(DATASETS)} {'':>5} {format_size(total_size):<15}")
    print()
    print(f"Time elapsed: {elapsed_time:.1f} seconds")
    print()
    
    # Verify all files
    print("Verifying downloads...")
    print("-" * 70)
    
    all_valid = True
    for key, dataset in DATASETS.items():
        filename = dataset['filename']
        filepath = os.path.join(OUTPUT_DIR, filename)
        valid, message = verify_file(filepath)
        
        status = "✓" if valid else "✗"
        print(f"  {status} {filename:<35} {message}")
        
        if not valid:
            all_valid = False
    
    print()
    
    # Final status
    if all_valid and success_count == len(DATASETS):
        print("╔" + "="*68 + "╗")
        print("║" + " "*20 + "✅ ALL DOWNLOADS SUCCESSFUL!" + " "*20 + "║")
        print("╚" + "="*68 + "╝")
        print()
        print("📁 All files saved in:", os.path.abspath(OUTPUT_DIR))
        print()
        print("🎯 NEXT STEPS:")
        print("   1. Download BTS delay data manually from:")
        print("      https://transtats.bts.gov/OT_Delay/OT_DelayCause1.asp?20=E")
        print("      (Select date range 2023-2024 and download)")
        print()
        print("   2. Save BTS file as: data/raw/bts_airline_delays.csv")
        print()
        print("   3. Run: python read_datasets.py")
        print("      (to explore the datasets)")
        print()
        print("   4. Run: python merge_datasets.py")
        print("      (to combine all datasets)")
        print()
        
    elif success_count > 0:
        print("⚠️  PARTIAL SUCCESS")
        print()
        print(f"   {success_count}/{len(DATASETS)} files downloaded successfully.")
        print("   Some downloads failed. Check the errors above and try again.")
        print()
        
    else:
        print("❌ ALL DOWNLOADS FAILED")
        print()
        print("   Please check your internet connection and try again.")
        print("   Or download manually using the links in ALL_DOWNLOAD_LINKS.txt")
        print()
    
    print("="*70)
    print()

# ============================================================================
# RUN SCRIPT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user.")
        print("   Run the script again to resume.\n")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("   Please report this issue or download manually.\n")

