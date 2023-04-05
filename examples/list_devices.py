import asyncio

import pyecodan


async def main():
    async with pyecodan.Client() as client:
        devices = {device.name : device for device in await client.list_devices()}
        print(devices)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
