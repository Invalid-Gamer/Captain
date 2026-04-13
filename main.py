import time
import threading
from Sensoren import ADC
import Comm  # Das Modul Comm.py laden


def main():
    adc = ADC.ADC()

    # Threads starten
    # Wir referenzieren die Funktionen direkt im Modul Comm
    t1 = threading.Thread(target=Comm.connHandler, args=(adc,), daemon=True)
    t1.start()

    t2 = threading.Thread(target=Comm.udpHandler, daemon=True)
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Sperre...")


if __name__ == '__main__':
    main()