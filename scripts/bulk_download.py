#!/usr/bin/env python3
"""Bulk download historical FuelWatch WA data for multiple locations.

This script downloads historical data for multiple locations and fuel types
in a single run, with rate limiting to avoid overwhelming the API.

Usage:
    python scripts/bulk_download.py --config locations.yaml --start-date 2023-01-01 --end-date 2024-12-31
    
Or specify locations directly:
    python scripts/bulk_download.py --locations Perth,Fremantle,Joondalup --fuel-types diesel,premium_98 --start-date 2023-01-01 --end-date 2024-12-31
"""
import argparse
import logging
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed. Config file support disabled.")
    print("Install with: pip install pyyaml")
    yaml = None

# Import from the main download script
from download_historical import download_date_range, FUEL_TYPE_MAP

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)

DEFAULT_LOCATIONS = [
    "Perth", "Fremantle", "Joondalup", "Rockingham", "Mandurah",
    "Armadale", "Midland", "Cannington", "Morley", "Booragoon",
    "Canning Vale", "Subiaco", "Victoria Park", "Caversham",
]

DEFAULT_FUEL_TYPES = ["diesel", "premium_98", "ulp_91"]


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if not yaml:
        raise RuntimeError("PyYAML not installed. Cannot load config file.")
    
    with config_path.open('r') as f:
        return yaml.safe_load(f)


def bulk_download(
    locations: list[str],
    fuel_types: list[str],
    start_date: datetime,
    end_date: datetime,
    output_dir: Path,
    delay_seconds: int = 2,
):
    """Download historical data for multiple locations and fuel types."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total = len(locations) * len(fuel_types)
    current = 0
    
    _LOGGER.info(
        "Starting bulk download: %d locations × %d fuel types = %d total downloads",
        len(locations),
        len(fuel_types),
        total,
    )
    
    for location in locations:
        for fuel_type in fuel_types:
            current += 1
            
            _LOGGER.info(
                "[%d/%d] Downloading %s - %s",
                current,
                total,
                location,
                fuel_type,
            )
            
            output_file = output_dir / f"{location.lower().replace(' ', '_')}_{fuel_type}.csv"
            
            try:
                download_date_range(
                    location=location,
                    fuel_type=fuel_type,
                    start_date=start_date,
                    end_date=end_date,
                    output_file=output_file,
                )
                
                # Rate limiting - be nice to the API
                if current < total:
                    _LOGGER.debug("Waiting %d seconds before next download...", delay_seconds)
                    time.sleep(delay_seconds)
                    
            except Exception as err:
                _LOGGER.error(
                    "Failed to download %s - %s: %s",
                    location,
                    fuel_type,
                    err,
                )
                continue
    
    _LOGGER.info("Bulk download complete! Downloaded %d datasets to %s", total, output_dir)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Bulk download historical FuelWatch WA data')
    parser.add_argument(
        '--config',
        type=Path,
        help='YAML config file with locations and fuel_types lists',
    )
    parser.add_argument(
        '--locations',
        help='Comma-separated list of locations (e.g., Perth,Fremantle)',
    )
    parser.add_argument(
        '--fuel-types',
        help='Comma-separated list of fuel types (e.g., diesel,premium_98)',
    )
    parser.add_argument(
        '--all-locations',
        action='store_true',
        help='Download for all default WA locations',
    )
    parser.add_argument(
        '--all-fuel-types',
        action='store_true',
        help='Download for all fuel types',
    )
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('historical_data'),
        help='Output directory for CSV files',
    )
    parser.add_argument(
        '--delay',
        type=int,
        default=2,
        help='Delay in seconds between downloads (default: 2)',
    )
    
    args = parser.parse_args()
    
    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError as err:
        _LOGGER.error("Invalid date format: %s", err)
        sys.exit(1)
    
    if start_date > end_date:
        _LOGGER.error("Start date must be before end date")
        sys.exit(1)
    
    # Determine locations and fuel types
    locations = []
    fuel_types = []
    
    if args.config:
        config = load_config(args.config)
        locations = config.get('locations', [])
        fuel_types = config.get('fuel_types', [])
    else:
        if args.all_locations:
            locations = DEFAULT_LOCATIONS
        elif args.locations:
            locations = [loc.strip() for loc in args.locations.split(',')]
        else:
            _LOGGER.error("Must specify --locations, --all-locations, or --config")
            sys.exit(1)
        
        if args.all_fuel_types:
            fuel_types = list(FUEL_TYPE_MAP.keys())
        elif args.fuel_types:
            fuel_types = [ft.strip() for ft in args.fuel_types.split(',')]
        else:
            fuel_types = DEFAULT_FUEL_TYPES
    
    if not locations or not fuel_types:
        _LOGGER.error("No locations or fuel types specified")
        sys.exit(1)
    
    # Validate fuel types
    invalid_fuel_types = [ft for ft in fuel_types if ft not in FUEL_TYPE_MAP]
    if invalid_fuel_types:
        _LOGGER.error("Invalid fuel types: %s", invalid_fuel_types)
        _LOGGER.error("Valid types: %s", list(FUEL_TYPE_MAP.keys()))
        sys.exit(1)
    
    _LOGGER.info("Locations: %s", locations)
    _LOGGER.info("Fuel types: %s", fuel_types)
    _LOGGER.info("Date range: %s to %s", start_date.date(), end_date.date())
    _LOGGER.info("Output directory: %s", args.output_dir)
    
    bulk_download(
        locations=locations,
        fuel_types=fuel_types,
        start_date=start_date,
        end_date=end_date,
        output_dir=args.output_dir,
        delay_seconds=args.delay,
    )


if __name__ == "__main__":
    main()
