import ujson
import urequests

from modules.config import getISO8601Time, loadEnvVariablesForSender


def sendStats(aht):
    configSender = loadEnvVariablesForSender()
    url = configSender['hostServer']
    deviceIdName = configSender['deviceId']
    payload = getPayload(aht, deviceIdName)
    sendPayload(payload, url)

def sendPayload(payload, url):
    headers = {'Content-Type': 'application/json'}
    try:
        response = urequests.post(
            url+'/api/v1/stats/collect/temperature',
            data=ujson.dumps(payload),
            headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response body: {response.text}")

        response.close()
    except Exception as e:
        print(f"Fetched exception: {e}")

def getPayload(aht,deviceId):
    return {
        "timestamp": getISO8601Time(),
        "temp": round(aht.temperature, 2),
        "humidity": round(aht.relative_humidity, 2),
        "status": "up",
        "deviceId": deviceId
    }
