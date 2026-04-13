import digitalio
import pwmio
import pins

# Hardware EINMALIG initialisieren (Global)
_dir2 = digitalio.DigitalInOut(pins.DIR2)
_dir2.direction = digitalio.Direction.OUTPUT
_pwm2 = pwmio.PWMOut(pins.PWM2, frequency=1000, duty_cycle=0)

_dir1 = digitalio.DigitalInOut(pins.DIR1) # Angenommen pins.DIR1 existiert
_dir1.direction = digitalio.Direction.OUTPUT
_pwm1 = pwmio.PWMOut(pins.PWM1, frequency=1000, duty_cycle=0)

def vorwaerts(speed: float) -> None:
    # Richtung setzen
    _dir2.value = True
    # Geschwindigkeit begrenzen
    speed = max(0, min(100, speed))
    # Duty Cycle setzen (0-65535)
    _pwm2.duty_cycle = int(speed / 100 * 65535)

def rueckwaerts(speed: float) -> None:
    _dir2.value = False
    speed = max(0, min(100, speed))
    _pwm2.duty_cycle = int(speed / 100 * 65535)

def stop():
    _pwm1.duty_cycle = 0
    _pwm2.duty_cycle = 0