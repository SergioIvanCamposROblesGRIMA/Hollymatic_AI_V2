from pywizlight import wizlight, discovery


class wizlights:

    async def discover_lights():
        bulbs = await discovery.find_wizlights()
        if len(bulbs) == 0:
            print(bulbs)
            print("No bulbs found.")
            return
        else:
            print(bulbs)
            bulb = bulbs[0]
        light = wizlight(bulb.ip_address)

        return light