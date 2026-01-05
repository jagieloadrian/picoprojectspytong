import uasyncio as asyncio
import ujson as json

from modules.sender import getPayload


async def runServer(aht, deviceIdName):
    async def serveClient(reader, writer):
        requestLine = await reader.readline()
        while await reader.readline() != b"\r\n":
            pass  # avoid headers

        try:
            requestStr = requestLine.decode('utf-8')
        except UnicodeError:
            requestStr = requestLine.decode('utf-8', 'ignore')
        print("Request line:", requestStr)

        if 'GET /stats' in requestStr:
            state = getPayload(aht, deviceIdName)
            response = 'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n' + json.dumps(state)
        elif 'GET /health' in requestStr:
            response = 'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nOK'

        elif 'GET /' in requestStr or requestStr == 'GET / HTTP/1.1':
            response = 'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nBrian\'s Brain is running. Use /stats or /health'

        else:
            response = 'HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found'

        writer.write(response.encode())
        await writer.drain()
        await writer.wait_closed()

    server = await asyncio.start_server(serveClient, "0.0.0.0", 80)
    print("Server HTTP running on port 80")
    await server.wait_closed()
