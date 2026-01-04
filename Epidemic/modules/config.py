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