import logging
import schedule
import time

def status_meldung_thread(adc, gps):
    schedule.every(2).minutes.do(status,adc,gps)

    while True:
        schedule.run_pending()
        time.sleep(1)


def status(adc,gps):
    logging.info("====")
    logging.info("Status Meldung gestartet")
    logging.info(f"Akkustand: {adc.get_12voltage(1)}V {adc.get_ampere(0)}A")
    logging.info(f"Posi: {gps.get_lat()} {gps.get_lon()}")
    logging.info(f"Geschwindigkeit: {gps.get_speed_ms}")
    logging.info("Status Meldung Ende")
    logging.info("====")
    return