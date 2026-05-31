from comps.motors.motors import Motors
import globals
import logging
VELOCITY = 50
LENKUNG = 75
DEADZONE_POS = 1950
DEADZONE_NEG = 1750
MittelCordsRechts = 1.34
MittelCordsLinks = 1.4
def inputHandler(x,y, motors, adc):
    currentLenkung = adc.get_lenkung(2)
    if globals.current_mode == 1 or globals.current_mode == 2:
        if y > DEADZONE_POS:
            speed = ((y - DEADZONE_POS) / (4095 - DEADZONE_POS)) * VELOCITY
            speed = max(0.0, min(100.0, speed))
            motors.vorwaerts(speed)
        elif y < DEADZONE_NEG:
            speed = ((DEADZONE_NEG - y) / DEADZONE_NEG) * VELOCITY
            speed = max(0.0, min(100.0, speed))
            motors.rueckwaerts(speed)
        else:
            motors.stop()

        if x > DEADZONE_POS:
            if currentLenkung != 0.00:
                speed = ((x - DEADZONE_POS) / (4095 - DEADZONE_POS)) * LENKUNG
                speed = max(0.0, min(100.0, speed))
                motors.rechts(speed)
            else:
                motors.stoplenkung()
        elif x < DEADZONE_NEG:
            if currentLenkung > 2.48:
                motors.stoplenkung()
            else:
                speed = ((DEADZONE_NEG - x) / DEADZONE_NEG) * LENKUNG
                speed = max(0.0, min(100.0, speed))
                motors.links(speed)
        else:
            if currentLenkung <= MittelCordsLinks and currentLenkung >= MittelCordsRechts:
                   motors.stoplenkung()
            elif currentLenkung < MittelCordsRechts:
                if currentLenkung < 0.30:
                    speed = 100
                elif currentLenkung < 1.18:
                    speed = LENKUNG * 0.9
                else:
                    speed = LENKUNG * 0.50
                motors.links(speed)
            elif currentLenkung > MittelCordsLinks:
                if currentLenkung > 2:
                    speed = 100
                elif currentLenkung > 1.70:
                    speed = LENKUNG * 0.9
                elif currentLenkung > 1.5:
                    speed = LENKUNG * 0.60
                else:
                    speed = LENKUNG * 0.50
                motors.rechts(speed)
    else:
        motors.stop()
        motors.stoplenkung()
        logging.debug(f"Mache nix weil current_mode: {globals.current_mode}")

def msgHanlder(msg):
    if ":" in msg:
        key, value = msg.split(":")
        if key == "mode":
            current_mode = value
        else:
            print(f"Keine Aktion zu key " + key + " konfiguriert!")
    else:
        print(f"Kein Befehl in TCP Nachricht erkannt: " + msg)