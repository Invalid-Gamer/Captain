import board
import digitalio
import globals
import time
import threading

class Hupe:
    def __init__(self) -> None:
        self.HupePin = digitalio.DigitalInOut(globals.HupePin)
        self.HupePin.direction = digitalio.Direction.OUTPUT
        self._impuls_laeuft = threading.Event()

    def _impulsHupeBlockierend(self):
        try:
            self.HupePin.value = True
            time.sleep(1)
        finally:
            self.HupePin.value = False
            self._impuls_laeuft.clear()

    def impulsHupe(self):
        if self._impuls_laeuft.is_set():
            return
        self._impuls_laeuft.set()
        threading.Thread(target=self._impulsHupeBlockierend, daemon=True).start()

    def setHupe(self, value: bool):
        self.HupePin.value = value