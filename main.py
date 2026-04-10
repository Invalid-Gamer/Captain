import time
import threading

from Sensoren import ADC
from Motor import motors
from Comm import Comm

def main():
    print("===Testmode ===")
    Comm.tcp_server_step()
    adc = ADC.ADC()


    t1 = threading.Thread(target=Comm.connhandler(), args=(adc, 0))
    t1.start()

    print(adc.get_ampere(0))
    print(adc.get_12voltage(1))


    print("===Dreht Motoren in 5Sek!===")
    time.sleep(5)

    motors.vorwaerts(30, 100)


    adc.de_ADC()
    print("===Testmode fertig!===")

if __name__ == '__main__':
    main()