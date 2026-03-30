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
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)

    if bssid:
        bssid_bytes = bytes.fromhex(bssid.replace(':', ''))
        wlan.connect(ssid, password, bssid=bssid_bytes)
        print(f"Connecting with BSSID: {bssid}")
    else:
        wlan.connect(ssid, password)
        print(f"Connecting with SSID: {ssid}")

    timeout = 0
    while not wlan.isconnected() and timeout < 40:
        print(f"Still try connect... ({timeout * 0.5}s)")
        time.sleep(0.5)
        timeout += 1

    if wlan.isconnected():
        wlan.config(hostname='iss_locator')
        print("Connected:", wlan.ifconfig())
        return True
    else:
        print("Failed to connect to WiFi after 20 seconds - check SSID, password, BSSID or network issues")
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