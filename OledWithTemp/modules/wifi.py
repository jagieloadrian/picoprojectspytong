import time

import network
import ntptime

from modules.config import loadEnvVariablesForWifi
from modules.displayFuncs import displayScroll


def connectToWifi(oled):
    wifiConfig = loadEnvVariablesForWifi()
    if wifiConfig is None:
        print("Could not load wifi configuration.")
        return False
    ssid = wifiConfig['ssid']
    password = wifiConfig['password']
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print("Connecting to wifi")
    wlan.connect(ssid, password)
    timeout = 15
    while timeout > 0:
        if wlan.status() == 3:
            print("Connected with WiFi. IP: ", wlan.ifconfig()[0])
            return True
        timeout -= 1
        displayScroll(oled=oled, lines=["Connecting to wifi...", f"Timeout will be in {timeout} seconds"], aht=None, delay=0.001)
        time.sleep(1)
    print("Could not connect with WiFI")
    return False

def syncTime():
    try:
        print("Synchronizing time with NTP...")
        ntptime.settime()
        print(f"Synchronized time: {time.localtime()}")
    except Exception as e:
        print("Error during synchronizing time:", e)
