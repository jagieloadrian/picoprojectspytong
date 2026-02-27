import network, time, os, ujson as json, ntptime

# ========== WIFI ==========
def connect_wifi():
    wifiConfig = loadEnvVariablesForWifi()
    if wifiConfig is None:
        print("Could not load wifi configuration, exit program")


    ssid = wifiConfig['ssid']
    password = wifiConfig['password']
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
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