from machine import Pin, SPI

from modules import gc9a01py

SPI_SCK = Pin(2)
SPI_MOSI = Pin(3)
TFT_CS   = Pin(1, Pin.OUT)
TFT_DC   = Pin(4, Pin.OUT)
TFT_RST  = Pin(6, Pin.OUT)
# TFT_BL  = 12


def getSpi():
    return SPI(0, baudrate = 30_000_000, polarity = 1, phase = 1, sck = SPI_SCK, mosi = SPI_MOSI)

def getDisplay(spi):
    return gc9a01py.GC9A01(spi=spi, cs=TFT_CS, dc=TFT_DC, reset=TFT_RST)