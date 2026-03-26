#!/usr/bin/env python3
"""Download historical FuelWatch WA data.

This script downloads historical fuel price data from FuelWatch WA
and saves it as CSV files for import into Home Assistant.

Usage:
    python download_historical.py --location Perth --fuel-type diesel --start-date 2024-01-01 --end-date 2024-12-31
"""
import argparse
import csv
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

try:
    from fuelwatcher import FuelWatch
except ImportError:
    print("Error: fuelwatcher library not found. Install with: pip install fuelwatcher")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)

FUEL_TYPE_MAP = {
    "ulp_91": 1,
    "premium_95": 2,
    "diesel": 4,
    "lpg": 5,
    "premium_98": 6,
    "e85": 10,
    "brand_diesel": 11,
}


def download_fuel_data(location: str, fuel_type: str, date: datetime) -> list:
    """Download fuel price data for a specific date."""
    product_id = FUEL_TYPE_MAP.get(fuel_type)
    if product_id is None:
        raise ValueError(f"Invalid fuel type: {fuel_type}")
    
    client = FuelWatch()
    try:
        client.query(suburb=location, product=product_id, day=date.strftime("%Y-%m-%d"))
        data = client.get_xml
        _LOGGER.info(
            "Downloaded %d stations for %s on %s",
            len(data) if data else 0,
            fuel_type,
            date.strftime("%Y-%m-%d")
        )
        return data if data else []
    except Exception as err:
        _LOGGER.error("Error downloading data for %s: %s", date.strftime("%Y-%m-%d"), err)
        return []


def calculate_statistics(data: list) -> dict:
    """Calculate statistics from raw fuel price data."""
    if not data:
        return None
    
    prices = []
    for row in data:
        try:
            if row.get("price") is not None:
                prices.append(float(row["price"]))
        except (TypeError, ValueError):
            continue
    
    if not prices:
        return None
    
    from statistics import mean
    
    min_price = min(prices)
    max_price = max(prices)
    avg_price = round(mean(prices), 2)
    
    cheapest = data[0]
    try:
        cheapest_price = float(cheapest.get("price")) if cheapest.get("price") is not None else None
    except (TypeError, ValueError):
        cheapest_price = None
    
    return {
        "min_price": min_price,
        "avg_price": avg_price,
        "max_price": max_price,
        "cheapest_price": cheapest_price,
        "station_count": len(data),
    }


def download_date_range(location: str, fuel_type: str, start_date: datetime, end_date: datetime, output_file: Path):
    """Download data for a date range and save to CSV."""
    current_date = start_date
    results = []
    
    _LOGGER.info("Downloading from %s to %s", start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    while current_date <= end_date:
        data = download_fuel_data(location, fuel_type, current_date)
        stats = calculate_statistics(data)
        
        if stats:
            results.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "location": location,
                "fuel_type": fuel_type,
                **stats
            })
        
        current_date += timedelta(days=1)
    
    # Write to CSV
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with output_file.open('w', newline='') as csvfile:
        fieldnames = ['date', 'location', 'fuel_type', 'min_price', 'avg_price', 'max_price', 'cheapest_price', 'station_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    _LOGGER.info("Saved %d records to %s", len(results), output_file)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Download historical FuelWatch WA data')
    parser.add_argument('--location', required=True, help='Suburb/location name')
    parser.add_argument('--fuel-type', required=True, choices=list(FUEL_TYPE_MAP.keys()), help='Fuel type')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', help='Output CSV file path (default: historical_data/<location>_<fuel_type>.csv)')
    
    args = parser.parse_args()
    
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError as err:
        _LOGGER.error("Invalid date format: %s", err)
        sys.exit(1)
    
    if start_date > end_date:
        _LOGGER.error("Start date must be before end date")
        sys.exit(1)
    
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = Path(f"historical_data/{args.location}_{args.fuel_type}.csv")
    
    download_date_range(args.location, args.fuel_type, start_date, end_date, output_file)
    _LOGGER.info("Download complete!")


if __name__ == "__main__":
    main()
