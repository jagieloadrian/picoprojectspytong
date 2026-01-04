import network
import socket

import ujson as json
import time
from machine import reset

from modules.devicetype import getAPTitle, DeviceType, getDeviceName

AP_PASSWORD = "haslo1234"

def scanNetworks():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    time.sleep(2)
    networks = wlan.scan()
    wlan.active(False)
    time.sleep(0.5)

    seen = set()
    unique_networks = []
    for net in networks:
        ssid = net[0].decode('utf-8').strip()
        if ssid and ssid not in seen:
            seen.add(ssid)
            secured = "🔓" if net[4] == 0 else "🔒"
            unique_networks.append((ssid, secured))

    unique_networks.sort(key=lambda x: x[0].lower())
    return unique_networks

def generateHtml(networks,device):
    options = '<option value="">-- Choose network --</option>'
    options += '<option value="manual">📝 Enter your network</option>'
    for ssid, icon in networks:
        safe_ssid = ssid.replace('"', '&quot;')
        options += f'<option value="{safe_ssid}">{icon} {ssid}</option>'

    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Pico Brian's Brain - WiFi Setup</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin: 40px; background: #f4f4f9; }}
                h1 {{ color: #333; }}
                .container {{ max-width: 360px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                select, input[type=text], input[type=password] {{ width: 100%; padding: 12px; margin: 12px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 16px; }}
                input[type=submit] {{ background: #4CAF50; color: white; padding: 14px; border: none; border-radius: 6px; cursor: pointer; font-size: 18px; margin-top: 20px; }}
                input[type=submit]:hover {{ background: #45a049; }}
                .manual {{ display: none; }}
                small {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1> Brian's Brain</h1>
                <p>Choose WiFI network or enter your own</p>
                <form action="/" method="post">
                    <select name="ssid" onchange="toggleManual(this)">
                        {options}
                    </select>
                    
                    <div id="manual-input" class="manual">
                        <input type="text" name="manual_ssid" placeholder="Network name (SSID)" autocomplete="off">
                    </div>
                    
                    <input type="password" name="password" placeholder="Password WiFi" required>
                    
                    <input type="submit" value="Save and connect">
                </form>
                <p><small>After saving {getDeviceName(device)} will restart.</small></p>
            </div>"""

# For pico2w
def startPortalPicoW(device):
    AP_SSID = getAPTitle(device)

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)

    print(f"AP started (Pico W): {AP_SSID}")

    networks = scanNetworks()
    print(f"Found {len(networks)} networks.")
    html_page = generateHtml(networks, device)

    runHttpServer(html_page, device)

# for esp32-c3
def startPortalEsp32C3(device):
    AP_SSID = getAPTitle(device)

    sta = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)

    if sta.active():
        sta.disconnect()
        sta.active(False)
    if ap.active():
        ap.active(False)

    time.sleep(3)

    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD, channel=6, authmode=network.AUTH_WPA_WPA2_PSK)
    time.sleep(2)

    print(f"AP started (ESP32-C3): {AP_SSID}")

    networks = scanNetworks()
    print(f"Found {len(networks)} networks.")
    html_page = generateHtml(networks, device)

    runHttpServer(html_page, device)

#  Common httpServer
def runHttpServer(html_page, device):
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print(f"Configuration portal running – connect to {getAPTitle(device)} and open browser")

    while True:
        try:
            client, addr = s.accept()
            print(f"Client connected from: {addr}")
            client.settimeout(8.0)

            request = b""
            try:
                while True:
                    chunk = client.recv(512)
                    if not chunk:
                        break
                    request += chunk
                    if len(request) > 4096:
                        break
            except OSError:
                pass

            try:
                request_str = request.decode('utf-8')
            except:
                request_str = request.decode('utf-8', 'ignore')

            body = ""
            if b"\r\n\r\n" in request:
                header_end = request.find(b"\r\n\r\n") + 4
                body_bytes = request[header_end:]
                body = body_bytes.decode('utf-8', 'ignore')

            if 'POST' in request_str.split('\n')[0]:
                params = {}
                for part in body.split('&'):
                    if '=' in part:
                        k, v = part.split('=', 1)
                        params[k] = v.replace('+', ' ').strip()

                ssid = params.get('ssid', '').strip()
                if ssid == 'manual':
                    ssid = params.get('manual_ssid', '').strip()
                password = params.get('password', '')

                if ssid:
                    try:
                        saveWifi(ssid, password)
                        print(f"Saved WiFi credentials for network: {ssid}")

                        success_html = f"""
                        <html><head><meta charset="utf-8"></head>
                        <body style="font-family:Arial;text-align:center;padding:50px;">
                        <h1>✅ Saved!</h1>
                        <p>Connecting to: <b>{ssid}</b></p>
                        <p>Restarting...</p>
                        </body></html>"""

                        response = 'HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' + success_html
                        client.send(response.encode('utf-8'))
                        client.close()
                        time.sleep(3)
                        print("Restarting device...")
                        reset()
                    except Exception as e:
                        print(f"Error saving config: {e}")
                        client.send(b"HTTP/1.0 500\r\n\r\nError saving config")
                else:
                    client.send(b"HTTP/1.0 400\r\n\r\nMissing SSID")

            else:
                response = 'HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' + html_page
                client.send(response.encode('utf-8'))

            client.close()
        except Exception as e:
            print(f"Error handling client: {e}")
            try:
                client.close()
            except:
                pass


def saveWifi(ssid, password):
    try:
        with open('env.json', 'r') as f:
            config = json.load(f)
    except (OSError, ValueError):
        config = {}

    config['ssid'] = ssid
    config['password'] = password

    try:
        with open('env.json', 'w') as f:
            json.dump(config, f)
        print(f"Saved WiFi credentials for network: {ssid}")
    except Exception as e:
        print(f"Error saving config: {e}")
#main func
def startPortal(device):
    if device == DeviceType.RPI_PICO_2W:
        print("Starting portal for pico2w")
        return startPortalPicoW(device)
    elif device == DeviceType.ESP32_C3:
        print("Starting portal for esp32-c3")
        return startPortalEsp32C3(device)
    else:
        return Exception("Not defined device")
