"""
written by Jannik Czinzoll
"""
import digitalio
import pwmio
import time

import pins


def vorwaerts(t: int, speed: int) -> None:
    dir2 = digitalio.DigitalInOut(pins.DIR2)
    dir2.direction = digitalio.Direction.OUTPUT

    pwm2 = pwmio.PWMOut(pins.PWM2, frequency=1000, duty_cycle=0)

    # true = vorwaerts
    dir2.value = True
    pwm2.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

    time.sleep(t)

    #stops and deinit things
    pwm2.duty_cycle = 0
    pwm2.deinit()
    dir2.deinit()

def rueckwaerts(t: int, speed: int) -> None:
    dir2 = digitalio.DigitalInOut(pins.DIR2)
    dir2.direction = digitalio.Direction.OUTPUT

    pwm2 = pwmio.PWMOut(pins.PWM2, frequency=1000, duty_cycle=0)

    # true = vorwaerts
    dir2.value = False
    pwm2.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

    time.sleep(t)

    #stops and deinit things
    pwm2.duty_cycle = 0
    pwm2.deinit()
    dir2.deinit()

def links(t: int, speed: int) -> None:
    dir1 = digitalio.DigitalInOut(pins.DIR2)
    dir1.direction = digitalio.Direction.OUTPUT

    pwm1 = pwmio.PWMOut(pins.PWM1, frequency=1000, duty_cycle=0)

    # true = vorwaerts
    dir1.value = False
    pwm1.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

    time.sleep(t)

    #stops and deinit things
    pwm1.duty_cycle = 0
    pwm1.deinit()
    dir1.deinit()
def rechts(t: int, speed: int):
    dir1 = digitalio.DigitalInOut(pins.DIR2)
    dir1.direction = digitalio.Direction.OUTPUT

    pwm1 = pwmio.PWMOut(pins.PWM1, frequency=1000, duty_cycle=0)

    # true = vorwaerts
    dir1.value = True
    pwm1.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

    time.sleep(t)

    #stops and deinit things
    pwm1.duty_cycle = 0
    pwm1.deinit()
    dir1.deinit()