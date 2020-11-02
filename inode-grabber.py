#!/usr/bin/env python3

import sys
import getopt
import asyncio
import pytz
import time
from bleak import discover
from influxdb import InfluxDBClient
from datetime import datetime

long_options = ["help", "mac", "config", "verbose"]
short_options = "hvd:c:"

input_mac="D0:CF:5E:03:93:16"

client = InfluxDBClient(host='nas.intra.lan', port=8086, database='black-hole')

def main():

    loop = asyncio.get_event_loop()
    ble_device = loop.run_until_complete(scan())

    e, p = decode_payload(ble_device)
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

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
    
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    power = power_int / impulses_int * 60.0
    print("Timestamp: " + str(timestamp))
    print("Current power: " + str(power) + " kW" )
    energy = energy_int / impulses_int
    print("Userd energy: " + str(energy) + " kWh")

    return(energy, power)

if __name__ == "__main__":
    main()
    time.sleep(5)
    
def push_metric():

    print("Nothing yet")
#json_body_1 = [
#    {
#        "measurement": "power",
#        "tags": {
#            "location": "home"
#        },
#        "time": timestamp,
#        "fields": {
#            "value": power
#        }
#    }
#]
#
#json_body_2 = [
#    {
#        "measurement": "energy",
#        "tags": {
#            "location": "home"
#        },
#        "time": timestamp,
#        "fields": {
#            "value": energy
#        }
#    }
#]
#client.write_points(json_body_1)
#client.write_points(json_body_2)
