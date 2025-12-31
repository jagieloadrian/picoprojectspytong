import ujson as json
import os

import network
import time

import ntptime

from modules.wifimanager import startPortal


def connectWifi():
    wifiConfig = loadEnvVariables()
    if wifiConfig is None:
        print("Could not load wifi configuration - starting configuration page")
        startPortal()
        return False
    ssid = wifiConfig['ssid']
    password = wifiConfig['password']
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    timeout = 15
    while timeout > 0:
        if wlan.status() == 3:
            print("Connect with WiFi. IP: ", wlan.ifconfig()[0])
            return True
        timeout -= 1
        time.sleep(1)
    print("Could not connect with WiFI")
    print("Starting configuration portal...")
    startPortal()
    return False


def loadEnvVariables():
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


def syncTime():
    try:
        print("Synchronizing time with NTP...")
        ntptime.settime()
        print(f"Synchronized time: {time.localtime()}")
    except Exception as e:
        print("Error during synchronizing time:", e)
