from machine import Pin, SPI
from modules.st7789py import ST7789

SCREEN_W = 240
SCREEN_H = 320

FPS = 30
FRAME_TIME = 1 / FPS

def getScreenConfig():
    # ========== TFT ==========
    spi = SPI(1,
              baudrate=80000000,
              polarity=1,
              phase=1,
              sck=Pin(12),
              mosi=Pin(11))

    return ST7789(
        spi,
        SCREEN_W,
        SCREEN_H,
        dc=Pin(9, Pin.OUT),
        cs=Pin(10, Pin.OUT),
        reset=Pin(8, Pin.OUT),
        rotation=0
    )
