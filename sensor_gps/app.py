import asyncio
import json
import random
from aiocoap import resource, Context, Message

lat = 48.8566
lon = 2.3522
battery = 100.0
temperature = 20.0


class GPSResource(resource.Resource):

    async def render_get(self, request):
        global lat, lon, battery, temperature

        lat += random.uniform(-0.0005, 0.0005)
        lon += random.uniform(-0.0005, 0.0005)

        battery = max(0, battery - random.uniform(0.1, 0.5))
        temperature += random.uniform(-0.2, 0.2)

        data = {
            "lat": lat,
            "lon": lon,
            "battery": round(battery, 2),
            "temperature": round(temperature, 2)
        }

        payload = json.dumps(data).encode("utf-8")
        return Message(payload=payload)


async def main():
    root = resource.Site()
    root.add_resource(['gps'], GPSResource())

    await Context.create_server_context(root, bind=("0.0.0.0", 5683))

    print("CoAP GPS Sensor running...")
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
