import digitalio
import pwmio
import logging
import globals
import time

class Motors:
    def __init__(self):
        self.dir2 = digitalio.DigitalInOut(globals.DIR2)
        self.dir2.direction = digitalio.Direction.OUTPUT
        self.pwm2 = pwmio.PWMOut(globals.PWM2, frequency=1000, duty_cycle=0)

        self.dir1 = digitalio.DigitalInOut(globals.DIR1)
        self.dir1.direction = digitalio.Direction.OUTPUT
        self.pwm1 = pwmio.PWMOut(globals.PWM1, frequency=1000, duty_cycle=0)

    def vorwaerts(self, speed: float) -> None:
        self.dir2.value = True
        self.pwm2.duty_cycle = int(speed / 100 * 65535)
        time.sleep(0.01)

    def rueckwaerts(self, speed: float) -> None:
        self.dir2.value = False
        self.pwm2.duty_cycle = int(speed / 100 * 65535)
        time.sleep(0.01)

    def stop(self) -> None:
        self.pwm2.duty_cycle = 0

    def stoplenkung(self):
        self.pwm1.duty_cycle = 0

    def links(self, speed: float) -> None:
        self.dir1.value = False
        self.pwm1.duty_cycle = int(speed / 100 * 65535)  # 16-bit: 0–65535
        time.sleep(0.01)

    def rechts(self, speed: float):
        self.dir1.value = True
        self.pwm1.duty_cycle = int(speed / 100 * 65535)  # 16-bit: 0–65535
        time.sleep(0.01)