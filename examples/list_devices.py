import asyncio

import pyecodan


async def main():
    async with pyecodan.Client() as client:
        devices = [device for device in await client.list_devices()]
        device = devices[0]
        print(device.name)

        await device.update()
        print(f"Flow Temperature: {device.flow_temperature}")

    async with pyecodan.Client() as client:
        device = await client.get_device("")
        print(device)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
