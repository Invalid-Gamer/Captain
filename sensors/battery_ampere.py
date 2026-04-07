"""
written by Jannik Czinzoll
"""
import time
import board
import busio
import digitalio
import pins

import adafruit_mcp3xxx.mcp3204 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn



SENSITIVITY = 0.185  # 5A Version
CAL_FACTOR = 0.74
OFFSET = 2.627

def initmcp():
    # spi init und cs pin festlegen
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(pins.CSPin)

    # MCP3204 initialisieren
    mcp = MCP.MCP3204(spi, cs)
    chan0 = AnalogIn(mcp, MCP.P0)
    return chan0

def readampere(chan: AnalogIn) -> float:
    voltage = chan.voltage

    current = ((voltage - OFFSET) / SENSITIVITY) * CAL_FACTOR
    print(f"{current:.2f}A")
    return current

