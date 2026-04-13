import time
import threading
from Sensoren import ADC, Batterie_Prozent
import Comm


def main():
    adc = ADC.ADC()

    # Threads für Kommunikation starten
    t1 = threading.Thread(target=Comm.connHandler, args=(adc,), daemon=True)
    t1.start()

    t2 = threading.Thread(target=Comm.udpHandler, daemon=True)
    t2.start()

    # Telemetrie Thread
    t3 = threading.Thread(target=Batterie_Prozent.collect_Bat_Prozent, args=(adc,), daemon=True)
    t3.start()

    print("--- System gestartet ---")

    # Haupt-Thread am Leben halten
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutdown...")


if __name__ == '__main__':
    main()