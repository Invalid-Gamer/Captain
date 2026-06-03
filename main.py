# Author: @Invalid-Gamer
import logging
import threading
import time

from comps.sensors import ADC, TOF # GPIO Daten
from comps.sensors import Globales_Navigationssatellitensystem as pyGPS
from communication import comms
from backend import logs, status_meldung, undervoltage, web_server
from comps.motors.motors import Motors
import globals

def main():
    logs.log_handler()

    logging.info("Versucht alle Sensoren zu starten ...")
    adc = ADC.ADC() # Analog to Digital
    tof = TOF.TOF() # Time of Flight Module
    gps = pyGPS.pyGPS() # GPS Modul
    motors = Motors() # Motors

    web_server.start_web_server(port=globals.web_server_port)

    def sensor_data_loop():
        while True:
            web_server.update_sensor_data(adc, tof, gps)
            time.sleep(1)

    sensor_thread = threading.Thread(target=sensor_data_loop, daemon=True)
    sensor_thread.start()

    logging.info("Startet 2min Status Meldung ...")
    status_meldung_thread = threading.Thread(target=status_meldung.status_meldung_thread,args=(adc,gps,tof,),daemon=True)
    status_meldung_thread.start()

    undervolt = threading.Thread(target=undervoltage.throttled, daemon=True)
    undervolt.start()

    t1 = threading.Thread(target=comms.connHandler, args=(adc,motors,tof,))
    t1.start()
    t2 = threading.Thread(target=comms.udpHandler, args=(adc,motors,))
    t2.start()

if __name__ == '__main__':
    main()