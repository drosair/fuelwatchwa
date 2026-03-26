# FuelWatch WA

The FuelWatch WA custom component provides fuel prices for petrol stations in Western Australia as sensors for Home Assistant.

The component uses the FuelWatch API to fetch petrol prices from petrol stations in Western Australia.

## Installation

### HACS Installation (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed and set up in Home Assistant
2. Add this repository to HACS:
   - Go to HACS → Integrations
   - Click the three-dot menu and select "Custom repositories"
   - Paste `https://github.com/drosair/fuelwatchwa` as the repository URL
   - Select "Integration" as the category
   - Click "Create"
3. Search for "FuelWatch WA" in HACS
4. Click "Install"
5. Restart Home Assistant

### Manual Installation

1. Download this repository as a ZIP file
2. Extract the contents to your Home Assistant `custom_components` directory as a folder named `fuelwatchwa`
3. Restart Home Assistant

## Configuration

After installing the component, you will need to configure it by going to the **Settings → Devices & Services** page and clicking **Create Integration** to add the FuelWatch WA integration.

You'll be prompted to configure:
- **Suburb**: The suburb in Western Australia where you want fuel prices
- **Product**: The fuel type (e.g., Unleaded 91, Premium 98, Diesel)
- **Day**: The day to fetch prices for (today, tomorrow, etc.)

## Sensors

The component creates sensors for the cheapest petrol station for your configured suburb:

- `fuel_station_name`: The brand of the petrol station
- `fuel_station_address`: The address of the petrol station
- `fuel_station_suburb`: The location of the petrol station
- `fuel_cheapest_price`: The price of the fuel at the petrol station

## Credits

- [FuelWatch](https://www.fuelwatch.wa.gov.au/) API provided by Government of Western Australia
- [FuelWatcher library](https://github.com/danielmichaels/fuelwatcher) by Daniel Michaels
