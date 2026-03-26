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

## [Unreleased]

### Planned
- Dashboard examples and UI improvements (Phase 2)
- Historical data analytics (Phase 3)
- CSV import/backfill utility (Phase 4)
- Location intelligence and GPS integration (Phase 5)
- CarPlay/mobile experience (Phase 6)
- Region and group support (Phase 7)

[0.2.0-alpha1]: https://github.com/drosair/fuelwatchwa/releases/tag/v0.2.0-alpha1
