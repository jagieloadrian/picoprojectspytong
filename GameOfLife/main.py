import asyncio
from machine import Pin

from modules.EpidemicModel import Epidemic
from modules.config import loadEnvVariablesForSender
from modules.sender import sendPayload
from modules.server import runServer
from modules.wifi import connectWifi, syncTime

onboard_led = Pin("LED", Pin.OUT)
async def runGame(gameInstance):
    saveInternal = 2
    while True:
        gameInstance.evolve()
        print(f"Run #{game.runCount} | Gen {game.generation} | "
              f"Infected: {game.stats['infected']} | Recovered: {game.stats['recovered']} | "
              f"Susceptible: {game.stats['susceptible']} | InfectedPct: {game.stats['infectedPct']}% | "
              f"RecoveredPct: {game.stats['recoveredPct']}%")
        if gameInstance.generation % saveInternal == 0:
            gameInstance.saveState()
        await sendStats(gameInstance)

        onboard_led.toggle()
        await asyncio.sleep(30)


async def sendStats(gameInstance):
    config = loadEnvVariablesForSender()
    url = config['hostServer']
    deviceId = config['deviceId']
    payload = gameInstance.getPostPayload(deviceId=deviceId)
    sendPayload(payload, url)


if connectWifi():
    syncTime()
    game = Epidemic()
    game.loadState()

    loop = asyncio.get_event_loop()
    loop.create_task(runServer(game))
    loop.create_task(runGame(game))
    loop.run_forever()
else:
    print("Not found Wifi - game isn't initialized")