import logging
import threading

from comps.sensors import ADC, Batterie_Prozent
from comps.sensors import Globales_Navigationssatellitensystem as pyGPS
from communication import comms
from backend import logs, status_meldung, undervoltage
import globals

def main():
    logs.log_handler()

    logging.info("Versucht alle Sensoren zu starten ...")
    adc = ADC.ADC()
    gps = pyGPS.pyGPS()

    logging.info("Startet 2min Status Meldung ...")
    status_meldung_thread = threading.Thread(target=status_meldung.status_meldung_thread,args=(adc,gps,),daemon=True)
    status_meldung_thread.start()

    undervolt = threading.Thread(target=undervoltage.throttled)
    undervolt.start()

    t1 = threading.Thread(target=comms.connHandler, args=(adc,))
    t1.start()
    t2 = threading.Thread(target=comms.udpHandler)
    t2.start()

    print(adc.get_ampere(0))
    print(adc.get_12voltage(1))

    t3 = threading.Thread(target=Batterie_Prozent.collect_Bat_Prozent, args=(adc,))
    t3.start()

if __name__ == '__main__':
    main()