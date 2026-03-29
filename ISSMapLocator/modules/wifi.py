import network, time, os, ujson as json, ntptime

# ========== WIFI ==========
def connect_wifi():
    wifiConfig = loadEnvVariablesForWifi()
    network.WLAN()
    if wifiConfig is None:
        print("Could not load wifi configuration, exit program")


    ssid = wifiConfig['ssid']
    password = wifiConfig['password']
    bssid = wifiConfig['bssid']
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if bssid:
        bssid_bytes = bytes.fromhex(bssid.replace(':', ''))
        wlan.connect(ssid, password, bssid=bssid_bytes)
        print(f"Connecting with BSSID: {bssid}")
    else:
        wlan.connect(ssid, password)

    wlan.config(hostname='iss_locator')
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Connected:", wlan.ifconfig())

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