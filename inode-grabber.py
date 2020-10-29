#!/usr/bin/env python3

import sys
import getopt
import asyncio
import pytz
import time
from bleak import discover
from influxdb import InfluxDBClient
from datetime import datetime

input_mac="D0:CF:5E:03:93:16"

client = InfluxDBClient(host='endpoint', port=8086, database='database')

async def scan():

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

def decode_payload(data):

    payload = list(*data.metadata["manufacturer_data"].values())
    payload_hex = [hex(x)[2:].zfill(2) for x in payload]

    print("Payload dec: " + str(payload))
    print("Payload hex: " + str(payload_hex))

    impulses_int = payload[6] + (payload[7] << 8)
    power_int = payload[0] + (payload[1] << 8) 
    energy_int = payload[2] + (payload[3] << 8) + (payload[4] << 16) + (payload[5] << 24)

    print("Impulses raw: " + str(impulses_int))
    print("Power raw: " + str(power_int))
    print("Energy raw: " + str(energy_int))
    
    power = power_int / impulses_int * 60.0
    print("Current power: " + str(power) + " kW" )
    energy = energy_int / impulses_int
    print("Userd energy: " + str(energy) + " kWh")

    return(energy, power)

def push_metric():

    print("Nothing")

def main():

    loop = asyncio.get_event_loop()
    ble_device = loop.run_until_complete(scan())

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    e, p = decode_payload(ble_device)

    push_metric(e,p,timestamp)

if __name__ == "__main__":
    main()
    time.sleep(5)
