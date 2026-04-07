"""
written by Jannik Czinzoll
Labor Vout Difference
15,5	3,314	4,677127339
14,6	3,129	4,666027485
14	2,995	4,674457429
13,5	2,887	4,676134396
13	2,781	4,67457749
12,5	2,676	4,671150972
12	2,569	4,671078241
11,5	2,455	4,684317719
11	2,356	4,66893039
10,5	2,239	4,689593569
10	2,153	4,644681839
9,5	2,033	4,672897196
9	1,927	4,670472237
8,5	1,824	4,660087719
8	1,723	4,643064423
7,5	1,626	4,612546125
7	1,509	4,638833665
6,5	1,404	4,62962963
6	1,29	4,651162791

	Durchschnitt	4,661935298
		4,66V
"""
import board
import busio
import digitalio
import pins

import adafruit_mcp3xxx.mcp3204 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn





def initmcp():
    # spi init und cs pin festlegen
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(pins.CSPin)

    # MCP3204 initialisieren
    mcp = MCP.MCP3204(spi, cs)
    chan1 = AnalogIn(mcp, MCP.P1)
    return chan1


VOLTAGE_FACTOR: float = 4.66
def readvoltage(chan: AnalogIn) -> float:
    voltage = chan.voltage
    volt = voltage * VOLTAGE_FACTOR
    print(f"{volt:.2f}A")
    return volt

