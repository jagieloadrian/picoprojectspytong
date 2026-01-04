import network
import time

import ntptime

from modules.config import loadEnvVariablesForWifi
from modules.devicetype import DeviceType
from modules.wifimanager import startPortal

def connectWifi(deviceType):
    if deviceType == DeviceType.RPI_PICO_2W:
        return connectToWifiByRpiPico2W(deviceType)
    elif deviceType == DeviceType.ESP32_C3:
        return connectToWifiByEsp32C3(deviceType)
    else:
        return Exception("Not defined device")

def connectToWifiByRpiPico2W(device):
    wifiConfig = loadEnvVariablesForWifi()
    if wifiConfig is None:
        print("Could not load wifi configuration - starting configuration page")
        startPortal(device)
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
        time.sleep(1)
    print("Could not connect with WiFI")
    print("Starting configuration portal...")
    startPortal(device)
    return False


def connectToWifiByEsp32C3(device):
    wifiConfig = loadEnvVariablesForWifi()
    if wifiConfig is None:
        print("Could not load wifi configuration - starting configuration page")
        startPortal(device)
        return False

    ssid = wifiConfig['ssid']
    password = wifiConfig['password']
    wlan = network.WLAN(network.STA_IF)
    resetInterfaces(wlan)
    wlan.config(txpower=8, reconnects=3)
    print("Connecting to Wi-Fi...")
    wlan.connect(ssid, password)

    timeout = 15
    while timeout > 0:
        if wlan.isconnected():
            print("Connected with Wi-Fi! IP:", wlan.ifconfig()[0])
            return True
        status = wlan.status()
        print(f"WLAN status: {status}")
        if status in (2, 3, 4):  # wrong pwd / no AP / fail
            print("Wi-Fi failed, doing full reset and retry...")
            wlan.disconnect()
            time.sleep(0.5)
            resetInterfaces(wlan)
            wlan.connect(ssid, password)
        time.sleep(1)
        timeout -= 1

    print("Could not connect with Wi-Fi")
    print("Starting configuration portal")
    startPortal(device)
    return False

def resetInterfaces(wlan):
    print("Resetting interfaces...")
    ap = network.WLAN(network.AP_IF)

    if wlan.active():
        wlan.disconnect()
        wlan.active(False)
        time.sleep(1.5)  # daj ESP32 czas na czyszczenie stanu
    if ap.active():
        ap.active(False)
        time.sleep(0.5)

    wlan.active(True)
    time.sleep(1)
def syncTime():
    try:
        print("Synchronizing time with NTP...")
        ntptime.settime()
        print(f"Synchronized time: {time.localtime()}")
    except Exception as e:
        print("Error during synchronizing time:", e)
