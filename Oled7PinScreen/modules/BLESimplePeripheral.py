import bluetooth
from .ble_advertising import advertising_payload
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_READ | _FLAG_NOTIFY,)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,)

_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX),)

class BLESimplePeripheral:
    def __init__(self, ble, display, name="Pico2W"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()
        self.received_text = None
        self._display = display

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            self._display.fill(0)
            self._display.text("Connected!", 0, 0)
            self._display.show()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            self._display.fill(0)
            self._display.text("Disconnected", 0, 0)
            self._display.text("Waiting...", 0, 12)
            self._display.show()
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                value = self._ble.gatts_read(self._rx_handle)
                text = value.decode("utf-8").strip()
                if text:
                    self.received_text = text
                    print("Received:", text)

    def _advertise(self, interval_us=100000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)