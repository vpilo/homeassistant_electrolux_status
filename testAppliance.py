import asyncio
import json
from pyelectroluxocp import OneAppApi
import re

# Fill in your username and password here :
login="damienbt@msn.com"
password="Ludivine1"

async def main():
    async with OneAppApi(login, password) as client:
        appliances = await client.get_appliances_list()
        print("get_appliances_list :\n",json.dumps(appliances, indent=2))

        info = await client.get_appliance_status(appliances[0].get("applianceId"))
        json_object = json.dumps(info, indent=2)
        print("get_appliance_status :\n", json_object)

        info = await client.get_appliance_capabilities(appliances[0].get("applianceId"))
        json_object = json.dumps(info, indent=2)
        print("get_appliance_capabilities :\n", json_object)

        # Writing to sample.json
        # with open("results.json", "w") as outfile:
        #     outfile.write(json_object)
        #
        # def state_update_callback(a):
        #     print("appliance state updated", json.dumps((a)))
        # await client.watch_for_appliance_state_updates([appliances[0].get("applianceId")], state_update_callback)

        #await asyncio.sleep(100)

asyncio.run(main())