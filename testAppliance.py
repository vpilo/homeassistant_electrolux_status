import asyncio
import json
from pyelectroluxocp import OneAppApi
import re
import os.path
from datetime import datetime

# Fill in your username and password here :
login="homeangelavalerio@gmail.com"
password="HuGHh%&7&x$sOND8f!fYq9ji"

def dump(name, json_data):
        json_object = json.dumps(json_data, indent=4)
        with open(f"samples/{name}.json", "w") as outfile:
            outfile.write(json_object)

async def main():
    async with OneAppApi(login, password) as client:
        appliances = await client.get_appliances_list()
        dump("get_appliances_list", appliances)

        info = await client.get_appliances_info([appliances[0].get("applianceId")])
        dump("get_appliances_info", info)

        info = await client.get_appliance_state(appliances[0].get("applianceId"))
        dump("get_appliance_state", info)

        info = await client.get_appliance_capabilities(appliances[0].get("applianceId"))
        dump("get_appliance_capabilities", info)
        
        def state_update_callback(update_json):
            print("appliance state updated")
            json_object = json.dumps(update_json, indent=4)
            now = str(datetime.now()).replace(" ", "_")
            dump(f"samples/update_{now}.json", json_object)

        await client.watch_for_appliance_state_updates([appliances[0].get("applianceId")], state_update_callback)
        await asyncio.sleep(1000)

asyncio.run(main())