from fuelwatcher import FuelWatch

class FuelWatchAPI:
    def __init__(self):
        self.client = FuelWatch()

    async def fetch(self, suburb: str, fuel_type: str, day: str):
        self.client.query(suburb=suburb, product=fuel_type, day=day)
        data = self.client.get_xml
        if not data:
            return None

        cheapest = data[0]

        return {
            "price": cheapest.get("price"),
            "brand": cheapest.get("brand"),
            "address": cheapest.get("address"),
            "location": cheapest.get("location"),
        }
