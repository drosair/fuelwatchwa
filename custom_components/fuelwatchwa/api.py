"""API client helpers for the FuelWatch WA integration."""
from __future__ import annotations

from datetime import UTC, datetime
from statistics import mean

from homeassistant.core import HomeAssistant
from fuelwatcher import FuelWatch

from .const import FUEL_TYPE_OPTIONS


class FuelWatchAPI:
    """Wrapper around fuelwatcher that returns normalized summary data."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    def _fetch_sync(self, location: str, fuel_type: str, day: str):
        """Run the blocking FuelWatch request synchronously."""
        product_id = FUEL_TYPE_OPTIONS[fuel_type]
        client = FuelWatch()
        client.query(suburb=location, product=product_id, day=day)
        return client.get_xml

    async def fetch(self, location: str, fuel_type: str, day: str) -> dict | None:
        """Fetch FuelWatch data and return summary statistics."""
        try:
            data = await self.hass.async_add_executor_job(
                self._fetch_sync, location, fuel_type, day
            )
        except Exception:
            return None

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

        min_price = min(prices)
        max_price = max(prices)
        avg_price = round(mean(prices), 2)
        price_spread = round(max_price - min_price, 2)
        cheapest = data[0]

        top_3 = []
        for row in data[:3]:
            try:
                price = float(row.get("price")) if row.get("price") is not None else None
            except (TypeError, ValueError):
                price = None

            top_3.append(
                {
                    "brand": row.get("brand"),
                    "price": price,
                    "address": row.get("address"),
                    "location": row.get("location"),
                }
            )

        try:
            cheapest_price = (
                float(cheapest.get("price")) if cheapest.get("price") is not None else None
            )
        except (TypeError, ValueError):
            cheapest_price = None

        return {
            "location": location,
            "fuel_type": fuel_type,
            "day": day,
            "fetched_at": datetime.now(UTC).isoformat(),
            "station_count": len(data),
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "price_spread": price_spread,
            "cheapest": {
                "price": cheapest_price,
                "brand": cheapest.get("brand"),
                "address": cheapest.get("address"),
                "location": cheapest.get("location"),
            },
            "top_3": top_3,
            "stations": data,
        }
