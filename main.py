import logging
import threading

from comps.sensors import ADC, Batterie_Prozent, TOF
from comps.sensors import Globales_Navigationssatellitensystem as pyGPS
from communication import comms
from backend import logs, status_meldung, undervoltage, webcamServer
from comps.motors.motors import Motors
import globals

def main():
    logs.log_handler()

    logging.info("Versucht alle Sensoren zu starten ...")
    adc = ADC.ADC() # Analog to Digital
    tof = TOF.TOF() # Time of Flight Module
    gps = pyGPS.pyGPS() # GPS Modul
    motors = Motors() # Motors

    logging.info("Startet 2min Status Meldung ...")
    status_meldung_thread = threading.Thread(target=status_meldung.status_meldung_thread,args=(adc,gps,tof,),daemon=True)
    status_meldung_thread.start()

    undervolt = threading.Thread(target=undervoltage.throttled)
    undervolt.start()

    t1 = threading.Thread(target=comms.connHandler, args=(adc,motors,tof,))
    t1.start()
    t2 = threading.Thread(target=comms.udpHandler, args=(adc,motors,))
    t2.start()
    t3 = threading.Thread(target=webcamServer.webcamServer)
    t3.start()

    print(adc.get_ampere(0))
    print(adc.get_12voltage(1))

    t3 = threading.Thread(target=Batterie_Prozent.collect_Bat_Prozent, args=(adc,))
    t3.start()

if __name__ == '__main__':
    main()