from time import sleep

from machine import Pin
from neopixel import NeoPixel


def main() -> None:
    count = 0
    ledPin = Pin(22)
    led = NeoPixel(ledPin, 1)
    while True:
        led[0] = (0,250,250)
        led.write()
        print(f"I'm a useless usb stick no {count}")
        sleep(1)
        led[0] = (0,0,250)
        led.write()
        print("Should filled blue")
        sleep(1)
        led[0] = (250,0,0)
        led.write()
        print("Should filled red")
        sleep(1)
        led[0] = (0,250,0)
        led.write()
        print("Should filled green")
        sleep(1)
        count += 1

if __name__ == "__main__":
    main()