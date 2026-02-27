import time

from machine import Pin
from neopixel import NeoPixel


def main() -> None:
    red = 0
    green = 0
    blue = 0
    max_lum = 100
    ledPin = Pin(21)
    rgb_led = NeoPixel(ledPin, 1)
    rgb_led.ORDER = (0, 1, 2, 3)
    print("RGB LED demo")

    while True:
        # Fade from black to red
        for i in range(0, max_lum):
            red = i
            blue = max_lum - i
            # Set the color of the NeoPixel
            rgb_led[0] = (red, green, blue)
            rgb_led.write()
            time.sleep_ms(10)

        time.sleep_ms(300)

        # Fade from red to yellow
        for i in range(0, max_lum):
            green = i
            red = max_lum - i
            # Set the color of the NeoPixel
            rgb_led[0] = (red, green, blue)
            rgb_led.write()
            time.sleep_ms(10)

        time.sleep_ms(300)

    # Fade from yellow to green
        for i in range(0, max_lum):
            blue = i
            green = max_lum - i
            # Set the color of the NeoPixel
            rgb_led[0] = (red, green, blue)
            rgb_led.write()
            time.sleep_ms(10)

        time.sleep_ms(300)

if __name__ == "__main__":
    main()