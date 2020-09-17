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


def main():

    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    print(argument_list)

    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print (str(err))
        sys.exit(2)

    loop = asyncio.get_event_loop()
    ble_device = loop.run_until_complete(scan())

    e, p = decode_payload(ble_device)
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

#    push_metric(e,p,timestamp)

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

def decode_payload(payload):

    # payload = {'uuids': [], 'manufacturer_data': {33444: [25, 0, 67, 204, 220, 0, 220, 5, 64, 0, 0]}}
  
    # [25, 0, 67, 204, 220, 0, 220, 5, 64, 0, 0]
    payload_rev = list(*payload.metadata["manufacturer_data"].values())
  
    # [0, 0, 64, 5, 220, 0, 220, 204, 67, 0, 25]
    payload_dec = list(reversed(payload_rev))
  
    # ['00', '00', '40', '05', 'dc', '00', 'dc', 'cc', '43', '00', '19']
    payload_hex = [hex(x)[2:].zfill(2) for x in payload_dec]
  
    print("payload dec rev: " + str(payload_rev))
    print("payload dec: " + str(payload_dec))
    print("payload hex: " + str(payload_hex))
  
    # extract payload content 
    # impulses      payload[3,4]
    # total energy  payload[5,6,7,8]
    # current power payload[9,10]
  
    impulses_hex = ''.join(payload_hex[3:5])
    power_hex = ''.join(payload_hex[9:11])
    energy_hex = ''.join(payload_hex[5:9])
    print("impulses hex: " + str(impulses_hex))
    print("power hex: " + str(power_hex))
    print("energy hex: " + str(energy_hex))
    
    impulses_dec = int(impulses_hex, 16)
    power_dec = int(power_hex, 16)
    energy_dec = int(energy_hex, 16)
    print("Impulses decimal: " + str(impulses_dec))
    print("Power decimal: " + str(power_dec))
    print("Energy decimal: " + str(energy_dec))
    
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    power = power_dec / impulses_dec * 60.0
    print("Timestamp: " + str(timestamp))
    print("Current power: " + str(power) + " kW" )
    energy = energy_dec / impulses_dec
    print("Userd energy: " + str(energy) + " kWh")

    return(energy, power)

if __name__ == "__main__":
    main()
    time.sleep(5)
    

def push_metric():

    print("Nothing")
