from emu import *

import logging
import sys
import os 
from datetime import datetime

Y2K = 946684800
int_max = 2**31-1
uint_max = 2**32-1

def get_timestamp(obj):
    return datetime.utcfromtimestamp(Y2K + int(obj.TimeStamp, 16)).isoformat()

def get_reading(reading, obj):
    reading = int(reading, 16) * int(obj.Multiplier, 16)
    if reading > int_max:
        reading = -1 * (uint_max - reading)
    return reading / float(int(obj.Divisor, 16))



def get_price(obj):
    return int(obj.Price, 16) / float(10 ** int(obj.TrailingDigits, 16))

def doLoop(client):

    client.start_serial()
    client.get_instantaneous_demand('Y')
    client.get_current_summation_delivered()

    last_demand = 0
    last_reading = 0

    while True:
        time.sleep(10)

        try:
            instantaneous_demand = client.InstantaneousDemand 
            timestamp = get_timestamp(instantaneous_demand)
            if timestamp > last_demand:
                measurement = [
                    {
                        "measurement": "demand",
                        "time": timestamp,
                        "fields": {
                            "demand": get_reading(instantaneous_demand.Demand, instantaneous_demand)
                        }
                    }
                ]
                last_demand = timestamp
                #DEBUG
                print(measurement)
        except AttributeError:
            pass 

        try:
            current_summation_delivered = client.CurrentSummationDelivered
            timestamp = get_timestamp(current_summation_delivered)
            if timestamp > last_reading:
                measurement = [
                    {
                        "measurement": "reading",
                        "time": timestamp,
                        "fields": {
                            "reading": get_reading(current_summation_delivered.SummationDelivered,
                                                   current_summation_delivered)
                        }
                    }
                ]
                last_reading = timestamp
                #DEBUG
                print(measurement)
        except AttributeError:
            pass

