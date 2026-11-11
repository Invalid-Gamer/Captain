# test_adc.py
# Kalibrier-Skript: gibt rohe ADC-Werte aller Kanäle aus,
# um VOLTAGE_FACTOR / OFFSET / CAL_FACTOR zu bestimmen.
# Beenden mit STRG+C

import time
import logging

from adc import ADC  # Pfad ggf. anpassen

logging.basicConfig(level=logging.ERROR)

POLL_INTERVAL = 0.5  # Sekunden zwischen den Messungen


def main() -> None:
    adc = ADC()
    print("Channel | Rohwert (12bit) | Chip-Spannung [V]")
    print("-" * 45)
    try:
        while True:
            line = []
            for ch in range(4):
                try:
                    raw = adc.get_chan_raw(ch)
                    volt = adc.get_chan_voltage(ch)
                    line.append(f"  CH{ch}: raw={raw:4d}  V={volt:6.3f}")
                except Exception as e:
                    line.append(f"  CH{ch}: Fehler: {e}")
            print(" |".join(line))
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nBeendet.")
    finally:
        adc.de_ADC()


if __name__ == "__main__":
    main()