from machine import Pin
import time

def main() -> None:
    led = Pin("LED", Pin.OUT)
    countNumb = 0

    while True:
        led.toggle()
        print(f"Świece we wszystkie strony razy {countNumb}")
        countNumb+=1
        time.sleep(0.5)


if __name__ == "__main__":
    main()