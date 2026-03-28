#!/usr/bin/env python3
"""Download historical FuelWatch WA CSV files from Azure blob storage.

FuelWatch provides monthly CSV files dating back to 2001.
This script downloads and processes them for import into Home Assistant.

Usage:
    # Download all available months
    python scripts/download_fuelwatch_csv.py --all --output-dir historical_data
    
    # Download specific date range
    python scripts/download_fuelwatch_csv.py --start 2023-01 --end 2024-12 --output-dir historical_data
    
    # Download single month
    python scripts/download_fuelwatch_csv.py --month 2024-03 --output-dir historical_data
"""
import argparse
import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)

FUELWATCH_CSV_URL = "https://warsydprdstafuelwatch.blob.core.windows.net/historical-reports/FuelWatchRetail-{month:02d}-{year}.csv"

# FuelWatch started publishing data in 2001
EARLIEST_YEAR = 2001
EARLIEST_MONTH = 12


def download_month_csv(year: int, month: int, output_dir: Path) -> Optional[Path]:
    """Download CSV file for a specific month."""
    url = FUELWATCH_CSV_URL.format(month=month, year=year)
    output_file = output_dir / f"FuelWatchRetail-{month:02d}-{year}.csv"
    
    _LOGGER.info("Downloading %s-%02d from %s", year, month, url)
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save CSV
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(response.content)
        
        # Count records
        with output_file.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            record_count = sum(1 for _ in reader)
        
        _LOGGER.info("Downloaded %s (%d records)", output_file.name, record_count)
        return output_file
        
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            _LOGGER.warning("No data available for %s-%02d", year, month)
        else:
            _LOGGER.error("HTTP error downloading %s-%02d: %s", year, month, err)
        return None
    except Exception as err:
        _LOGGER.error("Error downloading %s-%02d: %s", year, month, err)
        return None


def download_date_range(start_year: int, start_month: int, end_year: int, end_month: int, output_dir: Path):
    """Download all months in a date range."""
    current_year = start_year
    current_month = start_month
    downloaded = []
    
    while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
        result = download_month_csv(current_year, current_month, output_dir)
        if result:
            downloaded.append(result)
        
        # Move to next month
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
    
    _LOGGER.info("Downloaded %d files to %s", len(downloaded), output_dir)
    return downloaded


def download_all_available(output_dir: Path):
    """Download all available historical data from 2001 to current month."""
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    _LOGGER.info("Downloading all available data from %s-%02d to %s-%02d", 
                 EARLIEST_YEAR, EARLIEST_MONTH, current_year, current_month)
    
    return download_date_range(EARLIEST_YEAR, EARLIEST_MONTH, current_year, current_month, output_dir)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Download historical FuelWatch WA CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all available data (2001-present)
  python scripts/download_fuelwatch_csv.py --all --output-dir historical_data
  
  # Download specific year
  python scripts/download_fuelwatch_csv.py --start 2023-01 --end 2023-12
  
  # Download single month
  python scripts/download_fuelwatch_csv.py --month 2024-03
        """
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download all available data from 2001 to current month'
    )
    parser.add_argument(
        '--month',
        help='Download single month (format: YYYY-MM)'
    )
    parser.add_argument(
        '--start',
        help='Start month (format: YYYY-MM)'
    )
    parser.add_argument(
        '--end',
        help='End month (format: YYYY-MM)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('historical_data'),
        help='Output directory for CSV files (default: historical_data)'
    )
    
    args = parser.parse_args()
    
    if args.all:
        download_all_available(args.output_dir)
    elif args.month:
        try:
            date = datetime.strptime(args.month, "%Y-%m")
            download_month_csv(date.year, date.month, args.output_dir)
        except ValueError:
            _LOGGER.error("Invalid month format. Use YYYY-MM")
            sys.exit(1)
    elif args.start and args.end:
        try:
            start = datetime.strptime(args.start, "%Y-%m")
            end = datetime.strptime(args.end, "%Y-%m")
            download_date_range(start.year, start.month, end.year, end.month, args.output_dir)
        except ValueError:
            _LOGGER.error("Invalid date format. Use YYYY-MM")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    _LOGGER.info("Download complete!")


if __name__ == "__main__":
    main()
