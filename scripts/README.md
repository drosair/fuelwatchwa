# FuelWatch WA Historical Data Import

This directory contains utilities for importing historical fuel price data into Home Assistant.

## Requirements

```bash
pip install fuelwatcher
```

## Download Historical Data

### Option 1: Single Location (Individual Downloads)

Use the `download_historical.py` script to download historical data from FuelWatch:

```bash
python scripts/download_historical.py \
  --location Perth \
  --fuel-type diesel \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --output /config/historical_data/perth_diesel.csv
```

### Parameters

- `--location`: Suburb/location name (e.g., Perth, Fremantle)
- `--fuel-type`: One of: `ulp_91`, `premium_95`, `diesel`, `lpg`, `premium_98`, `e85`, `brand_diesel`
- `--start-date`: Start date in YYYY-MM-DD format
- `--end-date`: End date in YYYY-MM-DD format
- `--output`: (Optional) Output CSV file path

### Option 2: Bulk Download (Multiple Locations)

Download historical data for **multiple locations** at once:

```bash
# Download all default WA locations with all fuel types
python scripts/bulk_download.py \
  --all-locations \
  --all-fuel-types \
  --start-date 2023-01-01 \
  --end-date 2024-12-31 \
  --output-dir /config/historical_data

# Download specific locations and fuel types
python scripts/bulk_download.py \
  --locations Perth,Fremantle,Joondalup \
  --fuel-types diesel,premium_98 \
  --start-date 2023-01-01 \
  --end-date 2024-12-31

# Use a config file for complex setups
python scripts/bulk_download.py \
  --config scripts/locations_example.yaml \
  --start-date 2023-01-01 \
  --end-date 2024-12-31
```

**Features:**
- Rate limiting (2 second delay between downloads by default)
- Progress logging for each location/fuel type
- Creates separate CSV files for each combination
- Continues on error (won't stop entire batch if one fails)

**Parameters:**
- `--all-locations`: Download for 14 default WA suburbs
- `--all-fuel-types`: Download all 7 fuel types
- `--locations`: Comma-separated list of specific locations
- `--fuel-types`: Comma-separated list of specific fuel types
- `--config`: YAML config file (see `scripts/locations_example.yaml`)
- `--delay`: Seconds between downloads (default: 2)

### CSV Format

The scripts generate CSV files with the following columns:

```csv
date,location,fuel_type,min_price,avg_price,max_price,cheapest_price,station_count
2024-01-01,Perth,diesel,189.9,195.3,203.9,189.9,45
```

## Import into Home Assistant

Once you have the CSV file, use the Home Assistant service to import it:

### Via Developer Tools → Services

1. Go to **Developer Tools** → **Services**
2. Select service: `fuelwatchwa.import_historical_data`
3. Fill in the parameters:

```yaml
service: fuelwatchwa.import_historical_data
data:
  csv_path: /config/historical_data/perth_diesel.csv
  entity_id: sensor.perth_diesel_minimum_price
  source: FuelWatch Historical
```

### Via Automation

```yaml
automation:
  - alias: Import Perth Diesel Historical Data
    trigger:
      - platform: homeassistant
        event: start
    action:
      - service: fuelwatchwa.import_historical_data
        data:
          csv_path: /config/historical_data/perth_diesel.csv
          entity_id: sensor.perth_diesel_minimum_price
```

## Tips

### Bulk Download

Download multiple years of data in batches to avoid overwhelming the FuelWatch API:

```bash
# Download 2023
python scripts/download_historical.py \
  --location Perth --fuel-type diesel \
  --start-date 2023-01-01 --end-date 2023-12-31

# Download 2024
python scripts/download_historical.py \
  --location Perth --fuel-type diesel \
  --start-date 2024-01-01 --end-date 2024-12-31
```

### Import Path

The CSV file must be accessible by Home Assistant. Common locations:
- `/config/historical_data/` (if using HA OS/Supervised)
- Full absolute path if using Docker or other setups

### Verify Import

After importing, check the statistics:

1. Go to **Developer Tools** → **Statistics**
2. Search for your entity ID
3. Verify historical data appears in the graph

## Troubleshooting

### "File not found" Error
- Ensure the CSV path is accessible from within Home Assistant
- Use absolute paths, not relative paths
- Check file permissions

### No Data Imported
- Verify CSV file has valid data
- Check Home Assistant logs for errors
- Ensure Recorder is enabled

### Analytics Sensors Not Updating
- Analytics sensors need 2+ days of data
- Wait up to 1 hour for first analytics update
- Check sensor attributes for `data_points` count
