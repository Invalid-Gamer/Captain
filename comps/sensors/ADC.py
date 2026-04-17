"""
written by Jannik Czinzoll
"""
import board
import busio
import digitalio
import logging
import adafruit_mcp3xxx.mcp3204 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

import globals

VOLTAGE_FACTOR: float = 5.659637188
SENSITIVITY: float = 0.185  # 5A Version
CAL_FACTOR: float = 0.74
OFFSET: float = 2.627

class ADC:
    def __init__(self) -> None:
        # initialisiert den ADC und legt die Pins an, muss nur einmal ausgeführt werden; oder nach einen de_ADC()
        max_retries = 3
        #probiert maximal dreimal den Chip zu initialisieren
        for i in range(max_retries):
            try:
                # spi init und cs pin festlegen
                self.spi = busio.SPI(clock=globals.SPICLK, MISO=globals.SPIMISO, MOSI=globals.SPIMOSI)
                self.cs = digitalio.DigitalInOut(globals.CSPin)

                # MCP3204 initialisieren
                mcp = MCP.MCP3204(self.spi, self.cs)

                #chan2-3 wird im Moment nicht benutzt
                self.channels = {
                    0: AnalogIn(mcp, MCP.P0),
                    1: AnalogIn(mcp, MCP.P1),
                    2: AnalogIn(mcp, MCP.P2),
                    3: AnalogIn(mcp, MCP.P3),
                }
                return
            except Exception as e:
                logging.error(f"Exception while connecting to MCP3204: {e}")
        raise RuntimeError ("MCP connection failed")

    def de_ADC(self) -> None:
        #gibt die Pins wieder frei und schickt den ADC schlafen
        try:
            self.cs.value = False #low
            self.spi.deinit()
        except Exception:
            pass

    def get_12voltage(self, channel) -> float:
        #gibt einen float mit der aktuellen Batterie 12V Spannung zurück
        try:
            return round(self.channels[channel].voltage * VOLTAGE_FACTOR,2)
        except KeyError:
            raise ValueError("MCP nicht initialisiert oder falscher Channel?")
        except Exception as e:
            logging.error(f"Volt LeseError: {e}")
            raise

    def get_ampere(self, channel) -> float:
        #gibt einen float mit der aktuellen Batterie Stromstärke zurück
        try:
            return round(((self.channels[channel].voltage - OFFSET) / SENSITIVITY) * CAL_FACTOR, 2)
        except KeyError:
            raise ValueError("Ungültiger ADC Channel?")
        except Exception as e:
            logging.error(f"Ampere LeseError: {e}")
            raise

    def batterie_leer(self, channel) -> bool:
        # wird Wahr, wenn die Batteriespannung unter 11,8V fällt
        try:
            if round(self.channels[channel].voltage * VOLTAGE_FACTOR,2) <= 11.8:
                return True
            else:
                return False
        except KeyError:
            raise ValueError("Ungültiger ADC Channel?")
        except Exception as e:
            logging.error(f"Volt LeseError: {e}")
            raise

    def get_chan_voltage(self, channel) -> float:
        # gibt die Spannung auf einen Channel als Float aus
        try:
            return round(self.channels[channel].voltage,2)
        except KeyError:
            raise ValueError("Ungültiger ADC Channel?")
        except Exception as e:
            logging.error(f"Voltage LeseError: {e}")
            raise

    def get_chan_raw(self, channel) -> int:
        #gibt den 12-Bit ADC Wert zurück
        try:
            return self.channels[channel].value
        except KeyError:
            raise ValueError("Ungültiger ADC Channel?")
        except Exception as e:
            logging.error(f"LeseError: {e}")
            raise