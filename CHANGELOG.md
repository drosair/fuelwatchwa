# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0-alpha1] - 2026-03-26

### Added
- Initial HACS-ready release
- Config flow for UI-based setup
- Multi-fuel type support (7 fuel types)
- 8 sensors per fuel type (min/max/avg/spread/count + cheapest details)
- Async-safe API using Home Assistant executor jobs
- Example dashboard YAML
- Comprehensive documentation

### Fixed
- Blocking call detection in event loop
- Graceful handling of empty/malformed FuelWatch responses
- Correct fuel type product mappings per FuelWatch RSS specification

### Technical
- Async-first architecture with DataUpdateCoordinator
- 30-minute polling interval
- Stateless API layer
- Proper error handling and logging

## [0.2.1] - 2026-03-26

### Added
- Device grouping: each fuel type creates a logical device
- Enhanced sensor metadata with contextual icons
- Proper units (AUD/L, stations) for all sensors
- State class support for long-term statistics
- Device class MONETARY for price sensors
- Better sensor naming (e.g., "Minimum Price" vs "min_price")
- Availability tracking based on coordinator success
- Updated dashboard examples with new entity naming
- Auto-entities example in dashboard YAML

### Changed
- Entity IDs now include location: `sensor.{location}_{fuel_type}_{sensor_name}`
- Sensor names are more user-friendly
- Dashboard examples use 'perth' as location placeholder

### Improved
- Home Assistant Recorder integration for long-term analytics
- Better organization in UI with device grouping
- Historical graphing support with state_class
- Documentation with device grouping examples

## [0.3.0] - 2026-03-26

### Added
- Automatic fetching of both today's and tomorrow's prices
- Tomorrow's price summary in sensor attributes (available after 2:30pm)
- Price change calculation (tomorrow vs today)
- Suburb dropdown selector with 40+ common WA suburbs
- Fuel type multi-select dropdown with friendly names
- Custom suburb entry support

### Changed
- Removed 'day' selector from config flow (now fetches both automatically)
- Simplified configuration flow with better UX
- Tomorrow data gracefully handled when not yet available

### Breaking Changes
- Config flow changed - existing integrations need reconfiguration
- 'day' field removed from config (migration required for existing setups)

## [Unreleased]

### Planned
- Historical data analytics (Phase 3)
- CSV import/backfill utility (Phase 4)
- Location intelligence and GPS integration (Phase 5)
- CarPlay/mobile experience (Phase 6)
- Region and group support (Phase 7)

[0.2.0-alpha1]: https://github.com/drosair/fuelwatchwa/releases/tag/v0.2.0-alpha1
