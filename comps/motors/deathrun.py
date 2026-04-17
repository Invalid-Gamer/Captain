"""
written by Jannik Czinzoll
"""
import digitalio
import pwmio
import time

import globals

#baby burn baby burn
def deathrun(t: int, dir: bool, speed: int) -> None:
    dir2 = digitalio.DigitalInOut(globals.DIR2)
    dir2.direction = digitalio.Direction.OUTPUT

    pvm2 = pwmio.PVMOUT(globals.PVM2, frequency=1000, duty_cycle=0)

    # true = vorwaerts
    dir2.value = dir
    pvm2.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

    time.sleep(t)

    #stops and deinit things
    pvm2.duty_cycle = 0
    pvm2.deinit()
    dir2.deinit()



