"""API client helpers for the FuelWatch WA integration."""
from __future__ import annotations

from datetime import UTC, datetime
from statistics import mean

from fuelwatcher import FuelWatch

from .const import FUEL_TYPE_OPTIONS


class FuelWatchAPI:
    """Wrapper around fuelwatcher that returns normalized summary data."""

    def __init__(self) -> None:
        self.client = FuelWatch()

    async def fetch(self, location: str, fuel_type: str, day: str) -> dict | None:
        """Fetch FuelWatch data and return summary statistics."""
        product_id = FUEL_TYPE_OPTIONS[fuel_type]
        self.client.query(suburb=location, product=product_id, day=day)
        data = self.client.get_xml

        if not data:
            return None

        prices = [float(row["price"]) for row in data if row.get("price")]
        if not prices:
            return None

        min_price = min(prices)
        max_price = max(prices)
        avg_price = round(mean(prices), 2)
        price_spread = round(max_price - min_price, 2)
        cheapest = data[0]

        top_3 = [
            {
                "brand": row.get("brand"),
                "price": float(row.get("price")),
                "address": row.get("address"),
                "location": row.get("location"),
            }
            for row in data[:3]
            if row.get("price")
        ]

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
                "price": float(cheapest.get("price")),
                "brand": cheapest.get("brand"),
                "address": cheapest.get("address"),
                "location": cheapest.get("location"),
            },
            "top_3": top_3,
            "stations": data,
        }
