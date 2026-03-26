#!/usr/bin/env python3
"""Process FuelWatch historical CSV files for Home Assistant import.

This script reads FuelWatch CSV files (monthly exports) and generates
location/fuel-specific CSV files ready for HA import.

FuelWatch CSV columns:
- Serial No, Brand, Site Features, Address, Phone Number, Latitude, Longitude,
- Site Name, Product Description, Price, Date Published, Suburb, Region, 
- Postcode, Trading Name, Product ID, Supplier

Usage:
    # Process single file
    python scripts/process_fuelwatch_csv.py \
        --input historical_data/FuelWatchRetail-03-2024.csv \
        --output processed_data
    
    # Process all files in directory
    python scripts/process_fuelwatch_csv.py \
        --input-dir historical_data \
        --output processed_data \
        --location Caversham \
        --fuel-types diesel,premium_98
"""
import argparse
import csv
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)

# Map FuelWatch Product Description to our fuel type keys
FUEL_TYPE_MAP = {
    "Unleaded Petrol": "ulp_91",
    "Premium Unleaded 95": "premium_95",
    "Diesel": "diesel",
    "LPG": "lpg",
    "Premium Unleaded 98": "premium_98",
    "E85": "e85",
    "Brand diesel": "brand_diesel",
    # Older format variations
    "ULP": "ulp_91",
    "PULP": "premium_95",
    "98 RON": "premium_98",
    "LRP": "ulp_91",  # Leaded Replacement Petrol (treat as ULP)
}


def parse_fuelwatch_csv(csv_path: Path) -> List[Dict]:
    """Parse FuelWatch CSV file."""
    records = []
    
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Parse the date - try both old and new formats
                date_str = row.get('PUBLISH_DATE', row.get('Date Published', '')).strip()
                if not date_str:
                    continue
                
                # Try multiple date formats
                date = None
                for fmt in ["%d/%m/%Y %I:%M:%S %p", "%d/%m/%Y"]:
                    try:
                        date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if not date:
                    continue
                
                # Map fuel type - try both column names
                product_desc = row.get('PRODUCT_DESCRIPTION', row.get('Product Description', '')).strip()
                fuel_type = FUEL_TYPE_MAP.get(product_desc)
                if not fuel_type:
                    continue
                
                # Parse price - try both column names
                price_str = row.get('PRODUCT_PRICE', row.get('Price', '')).strip()
                if not price_str:
                    continue
                price = float(price_str)
                
                # Get location - try both column names
                suburb = row.get('LOCATION', row.get('Suburb', '')).strip()
                if not suburb:
                    continue
                
                records.append({
                    'date': date.date(),
                    'suburb': suburb,
                    'fuel_type': fuel_type,
                    'price': price,
                    'brand': row.get('BRAND_DESCRIPTION', row.get('Brand', '')).strip(),
                    'address': row.get('ADDRESS', row.get('Address', '')).strip(),
                })
                
            except (ValueError, TypeError) as err:
                _LOGGER.debug("Skipping invalid row: %s", err)
                continue
    
    return records


def aggregate_by_location_fuel_date(records: List[Dict]) -> Dict:
    """Aggregate records by location, fuel type, and date."""
    # Group by (suburb, fuel_type, date)
    grouped = defaultdict(list)
    
    for record in records:
        key = (record['suburb'], record['fuel_type'], record['date'])
        grouped[key].append(record['price'])
    
    # Calculate statistics for each group
    aggregated = {}
    for (suburb, fuel_type, date), prices in grouped.items():
        if not prices:
            continue
        
        key = f"{suburb}_{fuel_type}"
        if key not in aggregated:
            aggregated[key] = []
        
        aggregated[key].append({
            'date': date,
            'location': suburb,
            'fuel_type': fuel_type,
            'min_price': round(min(prices), 1),
            'avg_price': round(mean(prices), 1),
            'max_price': round(max(prices), 1),
            'cheapest_price': round(min(prices), 1),
            'station_count': len(prices),
        })
    
    return aggregated


def write_aggregated_csv(data: List[Dict], output_file: Path):
    """Write aggregated data to CSV."""
    if not data:
        _LOGGER.warning("No data to write")
        return
    
    # Sort by date
    data.sort(key=lambda x: x['date'])
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with output_file.open('w', newline='') as f:
        fieldnames = ['date', 'location', 'fuel_type', 'min_price', 'avg_price', 
                     'max_price', 'cheapest_price', 'station_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    _LOGGER.info("Wrote %d records to %s", len(data), output_file)


def process_file(input_file: Path, output_dir: Path, filter_location: str = None, 
                filter_fuel_types: List[str] = None):
    """Process a single FuelWatch CSV file."""
    _LOGGER.info("Processing %s", input_file.name)
    
    records = parse_fuelwatch_csv(input_file)
    _LOGGER.info("Parsed %d records from %s", len(records), input_file.name)
    
    if not records:
        return
    
    aggregated = aggregate_by_location_fuel_date(records)
    
    # Write separate files for each location/fuel combination
    for key, data in aggregated.items():
        location, fuel_type = key.split('_', 1)
        
        # Apply filters
        if filter_location and location.lower() != filter_location.lower():
            continue
        if filter_fuel_types and fuel_type not in filter_fuel_types:
            continue
        
        output_file = output_dir / f"{location.lower().replace(' ', '_')}_{fuel_type}.csv"
        
        # Append to existing file or create new
        if output_file.exists():
            # Read existing data
            existing = []
            with output_file.open('r') as f:
                reader = csv.DictReader(f)
                existing = list(reader)
            
            # Merge with new data, avoiding duplicates
            existing_dates = {row['date'] for row in existing}
            new_data = [d for d in data if str(d['date']) not in existing_dates]
            
            if new_data:
                all_data = existing + new_data
                # Convert date strings back to date objects for sorting
                for row in all_data:
                    if isinstance(row['date'], str):
                        row['date'] = datetime.strptime(row['date'], "%Y-%m-%d").date()
                write_aggregated_csv(all_data, output_file)
            else:
                _LOGGER.debug("No new data for %s", output_file.name)
        else:
            write_aggregated_csv(data, output_file)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Process FuelWatch historical CSV files')
    parser.add_argument('--input', type=Path, help='Input FuelWatch CSV file')
    parser.add_argument('--input-dir', type=Path, help='Directory containing FuelWatch CSV files')
    parser.add_argument('--output', type=Path, default=Path('processed_data'),
                       help='Output directory (default: processed_data)')
    parser.add_argument('--location', help='Filter by specific location/suburb')
    parser.add_argument('--fuel-types', help='Comma-separated list of fuel types to include')
    
    args = parser.parse_args()
    
    if not args.input and not args.input_dir:
        parser.error("Must specify --input or --input-dir")
    
    # Parse fuel types filter
    filter_fuel_types = None
    if args.fuel_types:
        filter_fuel_types = [ft.strip() for ft in args.fuel_types.split(',')]
    
    if args.input:
        process_file(args.input, args.output, args.location, filter_fuel_types)
    elif args.input_dir:
        csv_files = sorted(args.input_dir.glob('FuelWatchRetail-*.csv'))
        _LOGGER.info("Found %d CSV files to process", len(csv_files))
        
        for csv_file in csv_files:
            process_file(csv_file, args.output, args.location, filter_fuel_types)
    
    _LOGGER.info("Processing complete!")


if __name__ == "__main__":
    main()
