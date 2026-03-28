# Example Dashboards

This directory contains example Home Assistant dashboards for visualizing FuelWatch data.

## Available Dashboards

### 1. `simple_dashboard.yaml` - Basic Dashboard ✅ **Recommended**
Uses only built-in Home Assistant cards. No custom components required.

**Features:**
- Current price display (min/max/avg)
- Cheapest station info
- Analytics sensors (7-day, 30-day averages, trends)
- History graphs
- Tomorrow's forecast
- Quick links

### 2. `dashboard.yaml` - Advanced Dashboard
Enhanced dashboard with custom cards for better visualizations.

**Requires:**
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) (HACS)

**Features:**
- Everything from simple dashboard
- Advanced multi-series charts
- Gauges and statistics
- Location comparison charts
- Interactive map

## Important Notes

### Analytics Sensors
Analytics sensors (7-day average, 30-day average, price trend, volatility, weekly change) require **historical data** to function:

- **Option 1:** Wait 2-3 days for daily price data to accumulate naturally
- **Option 2:** Import historical CSV data using the import service (see main README)

The example dashboards handle missing analytics gracefully - they show helpful instructions instead of "Entity not found" errors.

### Multiple Fuel Types
The example dashboards show a single fuel type (diesel). To add multiple fuel types:

1. Add fuel types via **Settings** → **Devices & Services** → **FuelWatch WA** → **Configure**
2. Duplicate the fuel sections in the dashboard YAML
3. Replace `diesel` with your fuel type (e.g., `premium_98`, `ulp_91`)

## Installation

### Option 1: Import via UI (Easiest)

1. Open Home Assistant
2. Go to **Settings** → **Dashboards**
3. Click **⋮** (three dots) → **New dashboard**
4. Give it a name (e.g., "FuelWatch")
5. Click **⋮** → **Raw configuration editor**
6. Copy the contents of `simple_dashboard.yaml` or `dashboard.yaml`
7. Paste into the editor
8. Click **Save**

### Option 2: File-based Dashboard

1. Copy the dashboard file to your Home Assistant config directory:
   ```bash
   cp examples/simple_dashboard.yaml /config/dashboards/fuelwatch.yaml
   ```

2. Add to your `configuration.yaml`:
   ```yaml
   lovelace:
     mode: storage
     dashboards:
       fuelwatch:
         mode: yaml
         title: FuelWatch
         icon: mdi:gas-station
         filename: dashboards/fuelwatch.yaml
   ```

3. Restart Home Assistant

## Customization

**Replace location and fuel type:**

The examples use `caversham` and `diesel`. Find and replace with your entities:

```yaml
# Before
sensor.caversham_diesel_minimum_price

# After (for Perth and premium 98)
sensor.perth_premium_98_minimum_price
```

**Add multiple locations:**

You can monitor multiple locations by duplicating card sections and changing entity names.

## Dashboard Previews

### Simple Dashboard
Shows all essential information with standard HA cards:
- Current prices and cheapest station
- 7-day and 30-day analytics
- Price history graphs
- Tomorrow's forecast

### Advanced Dashboard
Adds enhanced visualizations:
- Gauge charts for quick price overview
- Multi-series ApexCharts for detailed trends
- Location comparison charts
- Interactive elements

## Tips

1. **Update every morning** - Prices update daily at ~2:30 AM
2. **Check tomorrow's forecast** - Available after 2:30 PM each day
3. **Use trend sensors** - `price_trend` shows if prices are rising/falling
4. **Monitor volatility** - High volatility = unpredictable prices
5. **Track weekly change** - Quick percentage change indicator

## Automation Ideas

Create automations using the dashboard data:

```yaml
# Notify when prices drop significantly
automation:
  - alias: "Low Fuel Price Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.caversham_diesel_minimum_price
        below: 180
    action:
      - service: notify.mobile_app
        data:
          message: "Diesel price dropped to {{ states('sensor.caversham_diesel_minimum_price') }}c/L!"
```

## Troubleshooting

**Entities not found:**
- Ensure the integration is configured and running
- Check entity names in **Developer Tools** → **States**
- Replace example entity names with your actual entities

**Charts not showing:**
- Wait 24 hours for initial data collection
- Check that Recorder is enabled
- Verify long-term statistics are being created

**Custom cards not working:**
- Install required custom cards via HACS
- Clear browser cache
- Check browser console for errors
