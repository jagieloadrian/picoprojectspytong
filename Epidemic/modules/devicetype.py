class DeviceType:
    RPI_PICO_2W = 1
    ESP32_C3 = 2

def getLedPin(type):
    if type == DeviceType.RPI_PICO_2W:
        print("Actual type is: RPI_PICO_2W")
        return "LED"
    elif type == DeviceType.ESP32_C3:
        print("Actual type is: ESP32_C3")
        return 2
    else:
        return Exception("Not defined device")

def getAPTitle(type):
    if type == DeviceType.RPI_PICO_2W:
        return 'PicoEpidemic-Setup'
    elif type == DeviceType.ESP32_C3:
        return 'ESP32C3Epidemic-Setup'
    else:
        return Exception("Not defined device")

def getDeviceName(type):
    if type == DeviceType.RPI_PICO_2W:
        return 'Pico 2W'
    elif type == DeviceType.ESP32_C3:
        return 'ESP32-C3'
    else:
        return Exception("Not defined device")