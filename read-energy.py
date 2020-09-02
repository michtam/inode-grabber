#!/usr/bin/env python3

import sys
import asyncio
from bleak import discover

input_mac="D0:CF:5E:03:93:16"

async def run():
    devices = await discover()
    print(*devices, sep = "\n")
    print("===============")
    for d in devices:
      if input_mac.lower() == d.address.lower():
        print(d)
        print(d.name)
        print(d.address)
        print(d.rssi)
        print(d.metadata)
        print("---------")
        return d
        break

    sys.exit("Device not found...")


loop = asyncio.get_event_loop()
ble_device = loop.run_until_complete(run())

payload_rev = list(*ble_device.metadata["manufacturer_data"].values())
payload_dec = list(reversed(payload_rev))
payload_hex = [hex(x)[2:] for x in payload_dec]
print(payload_rev)
print(payload_dec)
print(payload_hex)

# extract payload content
# impulses      payload[3,4]
# total energy  payload[5,6,7,8]
# current power payload[9,10]

impulses_hex = ''.join(payload_hex[3:5])
power_hex = ''.join(payload_hex[9:11])
energy_hex = ''.join(payload_hex[5:9])
print(impulses_hex)
print(power_hex)
print(energy_hex)

impulses_dec = int(impulses_hex, 16)
power_dec = int(power_hex, 16)
energy_dec = int(energy_hex, 16)
print(impulses_dec)
print(power_dec)
print(energy_dec)

power = power_dec / impulses_dec * 60.0
print("Current power: " + str(power) + " kW" )
energy = energy_dec / impulses_dec
print("Userd energy: " + str(energy) + " kWh")
