import board
import busio
import digitalio
import adafruit_vl53l0x
import time

class TOF:
    def __init__(self) -> None:
        i2c = busio.I2C(board.SCL, board.SDA)

        xshutvorne = digitalio.DigitalInOut(board.D4)  # GPIO4
        xshuthinten = digitalio.DigitalInOut(board.D17)  # GPIO27

        xshutvorne.direction = digitalio.Direction.OUTPUT
        xshuthinten.direction = digitalio.Direction.OUTPUT

        xshutvorne.value = False
        xshuthinten.value = False
        time.sleep(0.1)

        xshutvorne.value = True
        time.sleep(0.1)
        self.vorneTOF = adafruit_vl53l0x.VL53L0X(i2c)
        self.vorneTOF.set_address(0x30)

        xshuthinten.value = True
        time.sleep(0.1)
        self.hintenTOF = adafruit_vl53l0x.VL53L0X(i2c)
        self.hintenTOF.set_address(0x31)

    def get_mm_hinten(self) -> float:
        return self.hintenTOF.range

    def get_mm_vorne(self) -> float:
        return self.vorneTOF.range
