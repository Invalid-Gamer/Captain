import logging
import subprocess
import time


def throttled():
    #checkt alle 10 Sekunden, ob dem RasPi Spannung fehlt und gibt dieses aus
    while True:
        out = subprocess.check_output(
            ["vcgencmd", "get_throttled"]
        ).decode()

        value = int(out.split("=")[1],16)

        if value & 0x1:
            logging.warning("Main B Bus Undervolt !")

        if value & 0x10000:
            logging.warning("Main B Bus normal")

        time.sleep(10)