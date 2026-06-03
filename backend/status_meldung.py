# Authors: @ingressy, @Invalid-Gamer
import logging
import schedule
import time

from comps.sensors.TOF import TOF


# Alle möglichen Infos in den Logs alle 2 Minuten

def status_meldung_thread(adc, gps,tof):
    schedule.every(2).minutes.do(status,adc,gps,tof)

    while True:
        schedule.run_pending()
        time.sleep(1)


def status(adc,gps,tof): # Statusmeldung Func
    logging.info("====")
    logging.info("Statusmeldung gestartet")
    logging.info("---Akkus---")
    logging.info(f"Akkustand: {adc.get_12voltage(1)}V {adc.get_ampere(0)}A")
    logging.info("---Sensoren---")
    logging.info(f"Lenkung: {adc.get_lenkung(2)}")
    logging.info(f"Abstand Vorne: {tof.get_mm_vorne()}, Abstand Hinten: {tof.get_mm_hinten()}")
    logging.info("---GPS---")
    try:
        logging.info(f"Posi: {gps.get_lat()} {gps.get_lon()}")
        logging.info(f"Geschwindigkeit: {gps.get_speed_ms()}")
    except:
        logging.warning("GPS Modul nicht angeschlossen, überspringe GPS Daten")
    logging.info("Status Meldung Ende")
    logging.info("====")
    return