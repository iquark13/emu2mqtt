import json 
import paho.mqtt.client as mqtt
import threading
from emu2grab import *




'''Define inputs:

    mqttClient = useful name for logging
    mqttUser = user name for mqtt broker
    mqttPass = password for broker
    mqttHost = hostname or ip address for broker

    demandTopic = topic for posting demand info to
    usageTopic = topic for posting usage to

'''

mqttClient   = 'emu-2'
mqttUser    = 'mqtt'
mqttPass    = 'mqttpassword'
mqttHost    = 'homebox'

demandTopic = '/homeassistant/sensor/emu2/demand'
usageTopic  = '/homeassistant/sensor/emu2/usage'


#Connect to mqtt
first_connection = False #used for looping until connected

while first_connection==False:
    try:
        mqttc = mqtt.Client(client_id=mqttClient)
        mqttc.username_pw_set(mqttUser,password=mqttPass)
        mqttc.connect(mqttHost)
    except Exception as ex:
        print("MQTT Exception: " + str(ex))
        time.sleep(10)
    else:
        first_connection=True

#Setup some events for processing new values
demandEvent = threading.Event()
usageEvent  = threading.Event()
mqttEvent   = threading.Event()

#Termination Handling
loopEnable=True
termSig = False

#DataList (in liu of que)
dataList=[0,0]

def sendDemand():
    '''This function is a threaded function waiting for a signal
        that the demand is updated, and then queueing it to send 
        through mqtt
    '''
    jsonDict = {'demand':0}

    while termSig == False:
        if demandEvent.wait(timeout=11):
            jsonDict['demand']=dataList[0]
            while mqttEvent.isSet():
                time.sleep(.1)
            try:
                mqttEvent.set()
                mqttc.publish(demandTopic,json.dumps(jsonDict))
            except Exception as ex:
                print("MQTT Exception: " + str(ex))
            mqttEvent.clear()
            demandEvent.clear()

def sendUsage():
    '''This function is a threaded function waiting for a signal
        that the usage is updated, and then queueing it to send 
        through mqtt
    '''
    jsonDict = {'usage':0}

    while termSig == False:
        if usageEvent.wait(timeout=13):
            jsonDict['usage']=dataList[0]
            while mqttEvent.isSet():
                time.sleep(.1)
            try:
                mqttEvent.set()
                mqttc.publish(usageTopic,json.dumps(jsonDict))
            except Exception as ex:
                print("MQTT Exception: " + str(ex))
            mqttEvent.clear()
            usageEvent.clear()


#Create the main thread for sending mqtt messages
def main():
    threads =[]
    mqttc.loop_start() #Start the loop until termSig kills us
    t=threading.Thread(target=sendDemand)
    threads.append(t)
    t.start()

    t=threading.Thread(target=sendUsage)
    threads.append(t)
    t.start()
    
    t=threading.Thread(target=doLoop,args=((mqttc,dataList,termSig)))
    threads.append(t)
    t.start()

    while termSig==False:
        time.sleep(60)

if __name__ == "__main__":
    main()