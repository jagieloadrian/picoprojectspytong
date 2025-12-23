import bluetooth
from machine import Pin, I2C
import time

from modules.BLESimplePeripheral import BLESimplePeripheral
from modules.ssd1306 import SSD1306_I2C

def main() -> None:
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400 * 1000)
    display = SSD1306_I2C(128, 32, i2c)

    display.fill(0)
    display.text("BLE Starting...", 0, 10)
    display.show()

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