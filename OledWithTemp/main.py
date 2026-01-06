# Display Image & text on I2C driven ssd1306 OLED display
import asyncio
from asyncio import sleep

from machine import Pin, I2C

from modules.config import getISO8601Time, loadEnvVariablesForSender
from modules.displayFuncs import displayScroll
from modules.sender import sendStats
from modules.ssd1306 import SSD1306_I2C
from modules.ahtx0 import AHT10
from modules.wifi import connectToWifi, syncTime
from modules.server import runServer


def main() -> None:
    oled = getOledConfig()
    aht = getAht10Config()
    loop = asyncio.get_event_loop()
    configSender = loadEnvVariablesForSender()
    deviceIdName = configSender['deviceId']
    if connectToWifi(oled):
        syncTime()
        loop.create_task(displayScroll(oled, aht, delay=0.03))
        loop.create_task(sendStatsPeriodically(aht))
        loop.create_task(runServer(aht, deviceIdName))
    else:
        line = ["Could not connect with wifi... check configuration"]
        loop.create_task(displayScroll(oled=oled, lines=line, aht=None, delay=0.02))
    loop.run_forever()


def getAht10Config() -> AHT10:
    # I2C1 – AHT10
    i2c_aht = I2C(1, sda=Pin(2), scl=Pin(3), freq=100000)
    aht = AHT10(i2c_aht)
    return aht


def getOledConfig() -> SSD1306_I2C:
    # I2C0 – OLED
    WIDTH = 128  # oled display width
    HEIGHT = 32  # oled display height
    i2c_oled = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c_oled)
    return oled


async def sendStatsPeriodically(aht):
    while True:
        print("Temp:", round(aht.temperature,2), "Hum:", round(aht.relative_humidity,2), "Status:", aht.status, "Timestamp", getISO8601Time())
        sendStats(aht)

        await sleep(30)

if __name__ == "__main__":
    main()