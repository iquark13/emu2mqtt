from emu import *
from datetime import datetime
import sys

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

def doLoop(client,outputList,sigTerm,demandEvent,usageEvent):


    try:
        client.start_serial()
    except:
        print('Trouble starting serial. Sending sigterm')
        sigTerm=True
        sys.exit(1)
    client.get_instantaneous_demand('Y')
    client.get_current_summation_delivered()

    last_demand = 0
    last_reading = 0

    while sigTerm==False:
        time.sleep(10)

        try:
            instantaneous_demand = client.InstantaneousDemand 
            timestamp = get_timestamp(instantaneous_demand)
            if timestamp > last_demand:
                outputList[0]=get_reading(instantaneous_demand.Demand,
                                            instantaneous_demand)
                last_demand = timestamp
                demandEvent.set()
                #DEBUG
                print(outputList[0])

        except AttributeError:
            pass 

        try:
            current_summation_delivered = client.CurrentSummationDelivered
            timestamp = get_timestamp(current_summation_delivered)
            if timestamp > last_reading:
                outputList[1]=get_reading(current_summation_delivered.SummationDelivered,
                                            current_summation_delivered)
                last_reading = timestamp
                usageEvent.set()
                #DEBUG
                print(outputList[1])
        except AttributeError:
            pass

