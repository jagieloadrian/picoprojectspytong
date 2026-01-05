import asyncio
from time import sleep

from machine import Pin

from modules.EpidemicModel import Epidemic
from modules.config import loadEnvVariablesForSender
from modules.devicetype import getLedPin, getDeviceTypeFromConfig
from modules.sender import sendPayload
from modules.server import runServer
from modules.wifi import connectWifi, syncTime

device = getDeviceTypeFromConfig()
onboard_led = Pin(getLedPin(device), Pin.OUT)

async def runGame(gameInstance, config):
    saveInternal = 2
    while True:
        gameInstance.evolve()
        print(f"Run #{game.runCount} | Gen {game.generation} | "
              f"Infected: {game.stats['infected']} | Recovered: {game.stats['recovered']} | "
              f"Susceptible: {game.stats['susceptible']} | InfectedPct: {game.stats['infectedPct']}% | "
              f"RecoveredPct: {game.stats['recoveredPct']}%")
        if gameInstance.generation % saveInternal == 0:
            gameInstance.saveState()
        await sendStats(gameInstance, config)

        toggleLed()
        await asyncio.sleep(30)
def toggleLed():
    onboard_led.on()
    sleep(1)
    onboard_led.off()

async def sendStats(gameInstance, configSender):
    url = configSender['hostServer']
    deviceIdName = configSender['deviceId']
    payload = gameInstance.getPostPayload(deviceId=deviceIdName)
    sendPayload(payload, url)


if connectWifi(device):
    syncTime()
    game = Epidemic()
    game.loadState()
    config = loadEnvVariablesForSender()
    loop = asyncio.get_event_loop()
    deviceId = config['deviceId']
    loop.create_task(runServer(game, deviceId))
    loop.create_task(runGame(game, config))
    loop.run_forever()
else:
    print("Not found Wifi - game isn't initialized")