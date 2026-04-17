from comps.motors.motors import vorwaerts, rueckwaerts, stop, rechts, links, keineAhnungDigga
import globals
from globals import current_mode

VELOCITY = 50
LENKUNG = 75
DEADZONE_POS = 1950
DEADZONE_NEG = 1750
def inputHandler(x,y):
        if current_mode == 1 or current_mode == 2:
            if y > DEADZONE_POS:
                speed = ((y - DEADZONE_POS) / (4095 - DEADZONE_POS)) * VELOCITY
                speed = max(0.0, min(100.0, speed))
                vorwaerts(speed)
            elif y < DEADZONE_NEG:
                speed = ((DEADZONE_NEG - y) / DEADZONE_NEG) * VELOCITY
                speed = max(0.0, min(100.0, speed))
                rueckwaerts(speed)
            else:
                stop()

            if x > DEADZONE_POS:
                speed = ((x - DEADZONE_POS) / (4095 - DEADZONE_POS)) * LENKUNG
                speed = max(0.0, min(100.0, speed))
                rechts(speed)
            elif x < DEADZONE_NEG:
                speed = ((DEADZONE_NEG - x) / DEADZONE_NEG) * LENKUNG
                speed = max(0.0, min(100.0, speed))
                links(speed)
            else:
                keineAhnungDigga()
        else:
            stop()
            keineAhnungDigga()
def msgHanlder(msg):
    if ":" in msg:
        key, value = msg.split(":")
        if key == "mode":
            current_mode = value
        else:
            print(f"Keine Aktion zu key " + key + " konfiguriert!")
    else:
        print(f"Kein Befehl in TCP Nachricht erkannt: " + msg)