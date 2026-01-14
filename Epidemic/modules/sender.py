import urequests
import ujson


def sendPayload(payload, url):
    headers = {'Content-Type': 'application/json'}
    try:
        response = urequests.post(
            url+'/api/v1/stats/collect/epidemic',
            data= ujson.dumps(payload),
            headers= headers)
        print(f"Status code: {response.status_code}\n")
        print(f"Response body: {response.text}")

        response.close()
    except Exception as e:
        print(f"Fetched exception: {e}")
