import time
import threading

from Sensoren import ADC
from Motor import motors
from Comm import Comm

def main():
    print("===Testmode ===")
    t1 = threading.Thread(target=Comm.connHandler)
    t1.start()
    adc = ADC.ADC()

    print(adc.get_ampere(0))
    print(adc.get_12voltage(1))


    print("===Dreht Motoren in 5Sek!===")
    time.sleep(5)

    motors.vorwaerts(30, 100)


    adc.de_ADC()
    print("===Testmode fertig!===")

if __name__ == '__main__':
    main()