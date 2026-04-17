import digitalio
import pwmio
import time

import globals


def vorwaerts(speed: float) -> None:
    dir2 = digitalio.DigitalInOut(globals.DIR2)
    dir2.direction = digitalio.Direction.OUTPUT
    pwm2 = pwmio.PWMOut(globals.PWM2, frequency=1000, duty_cycle=0)
    # true = vorwaerts
    dir2.value = True
    pwm2.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

def rueckwaerts(speed: float) -> None:
    dir2 = digitalio.DigitalInOut(globals.DIR2)
    dir2.direction = digitalio.Direction.OUTPUT

    pwm2 = pwmio.PWMOut(globals.PWM2, frequency=1000, duty_cycle=0)

    # true = vorwaerts
    dir2.value = False
    pwm2.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

def stop():
    pwm2 = pwmio.PWMOut(globals.PWM2, frequency=1000, duty_cycle=0)
    pwm2.duty_cycle = 0

def links(speed: float) -> None:
    dir1 = digitalio.DigitalInOut(globals.DIR1)
    dir1.direction = digitalio.Direction.OUTPUT

    pwm1 = pwmio.PWMOut(globals.PWM1, frequency=1000, duty_cycle=0)

    # true = vorwaerts
    dir1.value = True
    pwm1.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

def rechts(speed: float):
    dir1 = digitalio.DigitalInOut(globals.DIR1)
    dir1.direction = digitalio.Direction.OUTPUT

    pwm1 = pwmio.PWMOut(globals.PWM1, frequency=1000, duty_cycle=0)

    # true = vorwaerts
    dir1.value = False
    pwm1.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

def keineAhnungDigga():
    pwm1 = pwmio.PWMOut(globals.PWM1, frequency=1000, duty_cycle=0)
    pwm1.duty_cycle = 0