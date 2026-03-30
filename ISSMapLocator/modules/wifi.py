import network, time, os, ujson as json, ntptime

# ========== WIFI ==========
def connect_wifi():
    wifiConfig = loadEnvVariablesForWifi()
    if wifiConfig is None:
        print("Could not load wifi configuration, exit program")

    ssid = wifiConfig['ssid']
    password = wifiConfig['password']
    bssid = wifiConfig['bssid']
    wlan = network.WLAN(network.STA_IF)
    resetInterfaces(wlan)
    wlan.config(txpower=8, reconnects=3)

    if bssid:
        bssid_bytes = bytes.fromhex(bssid.replace(':', ''))
        wlan.connect(ssid, password, bssid=bssid_bytes)
        print(f"Connecting with BSSID: {bssid}")
    else:
        wlan.connect(ssid, password)
        print(f"Connecting with SSID: {ssid}")

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
            time.sleep(1)
            resetInterfaces(wlan)
            if bssid:
                bssid_bytes = bytes.fromhex(bssid.replace(':', ''))
                wlan.connect(ssid, password, bssid=bssid_bytes)
                print(f"Connecting with BSSID: {bssid}")
            else:
                wlan.connect(ssid, password)
                print(f"Connecting with SSID: {ssid}")
        time.sleep(1)
        timeout -= 1
    else:
        print("Failed to connect to WiFi after 15 seconds - check SSID, password, BSSID or network issues")
        return False

def loadEnvVariablesForWifi():
    try:
        if 'env.json' not in os.listdir():
            print("Not found file env.json - could not connect  to WIFI!!")
            return None
        with open('env.json', 'r') as f:
            config = json.load(f)
            return {'ssid': config['ssid'],
                    'password': config['password'],
                    'bssid': config['bssid']}
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

def resetInterfaces(wlan):
    print("Resetting interfaces...")
    ap = network.WLAN(network.AP_IF)

    if wlan.active():
        wlan.disconnect()
        wlan.active(False)
        time.sleep(1.5)  # give ESP32 time for clear the state
    if ap.active():
        ap.active(False)
        time.sleep(0.5)

    wlan.active(True)
    time.sleep(1)