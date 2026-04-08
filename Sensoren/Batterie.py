"""
written by Jannik Czinzoll
"""
import board
import busio
import digitalio
import logging
import adafruit_mcp3xxx.mcp3204 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

import pins

VOLTAGE_FACTOR: float = 5.659637188
SENSITIVITY: float = 0.185  # 5A Version
CAL_FACTOR: float = 0.74
OFFSET: float = 2.627

def initmcp() -> tuple[AnalogIn, AnalogIn, AnalogIn, AnalogIn]:
    max_retries = 3
    #probiert maximal dreimal den Chip zu initialisieren
    for i in range(max_retries):
        try:
            # spi init und cs pin festlegen
            spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
            cs = digitalio.DigitalInOut(pins.CSPin)

            # MCP3204 initialisieren
            mcp = MCP.MCP3204(spi, cs)

            #chan2-3 wird im Moment nicht benutzt
            chan0 = AnalogIn(mcp, MCP.P0)
            chan1 = AnalogIn(mcp, MCP.P1)
            chan2 = AnalogIn(mcp, MCP.P2)
            chan3 = AnalogIn(mcp, MCP.P3)
            return chan0, chan1, chan2, chan3
        except Exception as e:
            logging.error(f"Exception while connecting to MCP3204: {e}")
    raise RuntimeError ("MCP connection failed")

def read_voltage(chan: AnalogIn) -> float:
    if chan is None:
        raise ValueError("MCP nicht initialisiert?")
    try:
        voltage = chan.voltage
        return round(voltage * VOLTAGE_FACTOR,2)
    except Exception as e:
        logging.error(f"Volt LeseError: {e}")
        raise

def read_ampere(chan: AnalogIn) -> float:
    if chan is None:
        raise ValueError("MCP nicht initialisiert?")
    try:
        voltage = chan.voltage
        return round(((voltage - OFFSET) / SENSITIVITY) * CAL_FACTOR, 2)
    except Exception as e:
        logging.error(f"Ampere LeseError: {e}")
        raise

def batterie_tiefenentladung(chan: AnalogIn) -> bool:
    if chan is None:
        raise ValueError("MCP nicht initialisiert?")
    try:
        voltage = chan.voltage
        volt = round(voltage * VOLTAGE_FACTOR,2)
        if volt >= 11.8:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Volt LeseError: {e}")
        raise