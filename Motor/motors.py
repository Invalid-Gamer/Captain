import digitalio
import pwmio
import pins

# Hardware einmalig beim Laden des Moduls starten
_dir2 = digitalio.DigitalInOut(pins.DIR2)
_dir2.direction = digitalio.Direction.OUTPUT
_pwm2 = pwmio.PWMOut(pins.PWM2, frequency=1000, duty_cycle=0)

def vorwaerts(speed: float) -> None:
    _dir2.value = True
    speed = max(0, min(100, speed))
    _pwm2.duty_cycle = int(speed / 100 * 65535)