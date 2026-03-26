from fuelwatcher import FuelWatch
from statistics import mean
from datetime import datetime

class FuelWatchAPIv2:
    def __init__(self):
        self.client = FuelWatch()

    async def fetch(self, suburb: str, fuel_type: str, day: str):
        self.client.query(suburb=suburb, product=fuel_type, day=day)
        data = self.client.get_xml

        if not data:
            return None

        prices = [float(row.get("price")) for row in data if row.get("price")]

        min_price = min(prices)
        max_price = max(prices)
        avg_price = round(mean(prices), 2)
        price_spread = round(max_price - min_price, 2)

        cheapest = data[0]

        top_3 = [
            {
                "brand": row.get("brand"),
                "price": row.get("price"),
                "address": row.get("address"),
                "location": row.get("location"),
            }
            for row in data[:3]
        ]

        return {
            "location": suburb,
            "fuel_type": fuel_type,
            "day": day,
            "fetched_at": datetime.utcnow().isoformat(),
            "station_count": len(data),
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "price_spread": price_spread,
            "cheapest": {
                "price": cheapest.get("price"),
                "brand": cheapest.get("brand"),
                "address": cheapest.get("address"),
                "location": cheapest.get("location"),
            },
            "top_3": top_3,
            "stations": data,
        }
