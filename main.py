import time

from Sensoren import battery_ampere
from Sensoren import Batterie
from motors import deathrun

def main():
    print("===Testmode ===")
    chan0, chan1, chan2, chan3 = Batterie.initmcp()

    battery_ampere.readampere(chan0)
    Batterie.read_voltage(chan1)
    time.sleep(0.5)
    deathrun.deathrun(5,True,25)




if __name__ == '__main__':
    main()