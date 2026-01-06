import time

import ujson as json
import os

def loadEnvVariablesForWifi():
    try:
        if 'env.json' not in os.listdir():
            print("Not found file env.json - could not connect  to WIFI!!")
            return None
        with open('env.json', 'r') as f:
            config = json.load(f)
            return {'ssid': config['ssid'],
                    'password': config['password']}
    except Exception as e:
        print("Error during read env.json:", e)
        return None

def loadEnvVariablesForSender():
    try:
        if 'env.json' not in os.listdir():
            print("Not found file env.json - could not prepare and send payload!!")
            return None
        with open('env.json', 'r') as f:
            config = json.load(f)
            return {'hostServer': config['hostServer'],
                    'deviceId': config['deviceId']}
    except Exception as e:
        print("Error during read env.json:", e)
        return None

def loadEnvVariablesDeviceType():
    try:
        if 'env.json' not in os.listdir():
            print("Not found file env.json - could not prepare and send payload!!")
            return None
        with open('env.json', 'r') as f:
            config = json.load(f)
            return {'deviceType': config['deviceType']}
    except Exception as e:
        print("Error during read env.json:", e)
        return None

def getISO8601Time():
    t = time.localtime()
    return  "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )