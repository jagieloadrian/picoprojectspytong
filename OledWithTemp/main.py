# Display Image & text on I2C driven ssd1306 OLED display
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import machine
import utime
import onewire, ds18x20, time


def main() -> None:
    ds_pin = machine.Pin(22)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    roms = ds_sensor.scan()

    print('Found DS devices: ', roms)

    WIDTH  = 128                                            # oled display width
    HEIGHT = 32                                             # oled display height

    i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=200000)       # Init I2C using pins GP8 & GP9 (default I2C0 pins)
    print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
    print("I2C Configuration: "+str(i2c))                   # Display I2C config


    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)                  # Init oled display


    while True:

        ds_sensor.convert_temp()
        time.sleep_ms(750)

        for rom in roms:

            print(rom)
            print(ds_sensor.read_temp(rom))

            # Clear the oled display in case it has junk on it.
            oled.fill(0)

            # Add some text
            oled.text("Temperature: ",12,8)
            oled.text(str(round(ds_sensor.read_temp(rom),2)),30,30)
            oled.text("*C",75,30)
            utime.sleep(2)


            # Finally update the oled display so the image & text is displayed
            oled.show()


if __name__ == "__main__":
    main()