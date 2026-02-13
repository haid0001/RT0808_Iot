import asyncio
import json
import random
from aiocoap import resource, Context, Message

temperature = 20.0

class TemperatureResource(resource.Resource):

    async def render_get(self, request):
        global temperature

        temperature += random.uniform(-0.2, 0.2)

        data = {
            "temperature": round(temperature, 2)
        }

        return Message(payload=json.dumps(data).encode())


async def main():
    root = resource.Site()
    root.add_resource(['temperature'], TemperatureResource())

    await Context.create_server_context(root, bind=("0.0.0.0", 5683))
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
