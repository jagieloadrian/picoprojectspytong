import asyncio
from machine import Pin

from modules.BriansBrain import BriansBrain, randomBrainCells
from modules.server import runServer
from modules.wifi import connectWifi, syncTime

onboard_led = Pin("LED", Pin.OUT)
async def runGame(gameInstance):
    saveInternal = 10
    while True:
        gameInstance.evolve()
        print(f"Run #{game.runCount} | Gen {game.generation} | "
              f"On: {game.stats['onCount']} | Dying: {game.stats['dyingCount']} | "
              f"Activity: {game.stats['activityPct']}%")
        if gameInstance.generation % saveInternal == 0:
            gameInstance.saveState()

        onboard_led.toggle()
        await asyncio.sleep(1)

if connectWifi():
    syncTime()
    initial_cells = randomBrainCells(200, 40)
    game = BriansBrain(initial_cells)
    game.loadState()

    loop = asyncio.get_event_loop()
    loop.create_task(runServer(game))
    loop.create_task(runGame(game))
    loop.run_forever()
else:
    print("Not found Wifi - game isn't initialized")