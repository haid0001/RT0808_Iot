import asyncio
import json
import random
from aiocoap import resource, Context, Message

battery = 100.0

class BatteryResource(resource.Resource):

    async def render_get(self, request):
        global battery

        battery = max(0, battery - random.uniform(0.1, 0.5))

        data = {
            "battery": round(battery, 2)
        }

        return Message(payload=json.dumps(data).encode())


async def main():
    root = resource.Site()
    root.add_resource(['battery'], BatteryResource())

    await Context.create_server_context(root, bind=("0.0.0.0", 5683))
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
