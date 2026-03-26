# 📜 Project History & Attribution

## Origins

This project was originally based on a fork of:

**fuelwatchwa** (original repository)

The original project provided a foundation for accessing FuelWatch WA data and inspired the initial direction of this integration.

---

## Evolution

Since the initial fork, this project has been significantly redesigned and expanded into a dedicated **Home Assistant custom integration**, including:

* Full Home Assistant integration structure (`custom_components`)
* Config Flow for UI-based setup
* Async-safe API handling (non-blocking)
* DataUpdateCoordinator pattern
* Multi-fuel support
* Summary and actionable sensors (cheapest station, averages, etc.)
* Planned support for dashboards, historical data, and analytics

The architecture, feature set, and long-term direction now differ substantially from the original implementation.

---

## Current Direction

This project is now an **independent initiative** focused on:

> Turning FuelWatch WA data into a practical, intelligent fuel decision system within Home Assistant.

The roadmap includes:

* Smart dashboards
* Historical price tracking
* Location-aware recommendations
* Mobile / CarPlay-friendly usage

---

## Attribution

We acknowledge and thank the original author(s) of the upstream project for their work and inspiration.

This project builds upon that foundation but has evolved into a standalone implementation with its own design, goals, and roadmap.

---

## Philosophy

This project aims to prioritise:

* Real-world usability over raw data
* Clean, maintainable architecture
* Home Assistant best practices (async, coordinator pattern)
* Extensibility for future analytics and automation

---
