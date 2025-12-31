import ujson as json
import uasyncio as asyncio


async def runServer(game):
    async def serveClient(reader, writer):
        requestLine = await reader.readline()
        while await reader.readline() != b"\r\n":
            pass  # avoid headers

        request = str(requestLine)
        if '/stats' in request:
            state = game.getStats()
            response = 'HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n' + json.dumps(state)
        else:
            response = 'HTTP/1.0 404 Not Found\r\nContent-type: text/plain\r\n\r\nNot Found'

        writer.write(response.encode())
        await writer.drain()
        await writer.wait_closed()

    server = await asyncio.start_server(serveClient, "0.0.0.0", 80)
    print("Server HTTP running on port 80")
    await server.wait_closed()
