import bluetooth
from machine import Pin, SPI
import time

from modules.BLESimplePeripheral import BLESimplePeripheral
from modules.ssd1306 import SSD1306_SPI


def main() -> None:
    print("Setup spi")
    spi = SPI(0, baudrate=500000, polarity=0, phase=0,
              sck=Pin(18),   # CLK
              mosi=Pin(19))  # DIN/MOSI

    cs = Pin(17, Pin.OUT)   # CS
    dc = Pin(16, Pin.OUT)   # D/C
    res = Pin(20, Pin.OUT)  # RES (opcjonalny)

    print("Setup display")
    display = SSD1306_SPI(128, 64, spi, dc, res, cs)

    res.value(0)
    time.sleep(0.1)
    res.value(1)
    time.sleep(0.1)

    display.fill(1)
    display.show()
    time.sleep(2)

    display.fill(0)
    display.text("BLE Starting...", 0, 10)
    display.show()
    print("Looking for ble devices...")
    ble = bluetooth.BLE()
    uart = BLESimplePeripheral(ble=ble, display=display)

    display_text = "Waiting for text..."
    x_pos = 128

    while True:
       if uart.received_text is not None:
            display_text = uart.received_text + "  "
            x_pos = 128
            uart.send("OK\n")
            uart.received_text = None
       x_pos = showText(display_text, display, x_pos)

def showText(text, display, xpos):
    text_length = len(text) * 8
    display.fill(0)
    display.text("-" * 127, 0, 0, 1)
    display.text(text, xpos, 11, 1)
    display.text("-" * 127, 0, 22, 1)
    display.show()
    xpos -= 2
    if xpos < -text_length:
        xpos = 128
    time.sleep(0.05)
    return xpos

if __name__ == "__main__":
    main()