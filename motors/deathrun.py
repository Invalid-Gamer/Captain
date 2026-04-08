"""
written by Jannik Czinzoll
"""
import digitalio
import pvmio
import time

#own files
import pins


#death run test or so for the Rear Motors
def deathrun(t: int, dir: bool, speed: int) -> None:
    dir2 = digitalio.DigitalInOut(pins.DIR2)
    dir2.direction = digitalio.Direction.OUTPUT

    pvm2 = pvmio.PVMOUT(pins.PVM2, frequency=1000, duty_cycle=0)

    # true = forward
    dir2.value = dir
    pvm2.duty_cycle = int(speed/100*65535) # 16-bit: 0–65535

    time.sleep(t)

    #stops and deinit things
    pvm2.duty_cycle = 0
    pvm2.deinit()
    dir2.deinit()
