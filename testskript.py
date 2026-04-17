import socket
import struct
import time
import digitalio
import pwmio
import globals  # Deine Pin-Definitionen (DIR2, PWM2, etc.)

# --- KONFIGURATION ---
UDP_PORT = 9005
TCP_PORT = 9006
DEADZONE = 1950  # Alles unter 1950 wird als Stillstand gewertet
DEADZONE_INV = 1750
MAX_ADC = 4095  # Maximalwert des ESP32 Joysticks (12-Bit)

# --- HARDWARE INITIALISIERUNG ---
print("[SYSTEM] Initialisiere Hardware...")
try:
    # Motor 2 (Fahrmotor)
    motor_dir = digitalio.DigitalInOut(globals.DIR2)
    motor_dir.direction = digitalio.Direction.OUTPUT
    servo_dir = digitalio.DigitalInOut(globals.DIR1)
    servo_dir.direction = digitalio.Direction.OUTPUT
    # Frequenz 1000Hz ist gut für die meisten Motortreiber
    motor_pwm = pwmio.PWMOut(globals.PWM2, frequency=1000, duty_cycle=0)
    servo_pwm = pwmio.PWMOut(globals.PWM1, frequency=1000, duty_cycle=0)

    print("[SYSTEM] Motor-Hardware bereit.")
except Exception as e:
    print(f"[FEHLER] Hardware-Initialisierung fehlgeschlagen: {e}")

# --- NETZWERK SETUP ---
# UDP für Joystick (schnell, verbindungslos)
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind(('0.0.0.0', UDP_PORT))
udp_sock.settimeout(0.01)

# TCP für Status (zuverlässig, bidirektional)
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind(('0.0.0.0', TCP_PORT))
tcp_server.listen(1)
tcp_server.setblocking(False)

active_conn = None


# --- LOGIK-FUNKTIONEN ---

def set_motor_speed(y_raw):
    """
    Berechnet die Geschwindigkeit basierend auf dem Joystick-Y-Wert.
    Skaliert von DEADZONE (0%) bis MAX_ADC (100%).
    """
    if y_raw > DEADZONE:
        # 1. Prozentualen Wert berechnen (0.0 bis 100.0)
        # Die Differenz zwischen Ist-Wert und Start-Grenze geteilt durch den verfügbaren Weg
        speed_pct = ((y_raw - DEADZONE) / (MAX_ADC - DEADZONE)) * 100
        speed_pct = max(0.0, min(100.0, speed_pct))  # Sicherheit: Wert begrenzen

        # 2. Hardware ansteuern
        motor_dir.value = True  # Vorwärts-Richtung

        # 3. In 16-Bit PWM umrechnen (CircuitPython nutzt 0 bis 65535)
        duty = int((speed_pct / 100) * 65535)
        motor_pwm.duty_cycle = duty

        return speed_pct
    elif y_raw < DEADZONE_INV:
        speed_pct = ((DEADZONE_INV - y_raw) / DEADZONE_INV) * 100
        speed_pct = max(0.0, min(100.0, speed_pct))

        motor_dir.value = False

        duty = int((speed_pct / 100) * 65535)
        motor_pwm.duty_cycle = duty
        return speed_pct
    else:
        # Joystick ist in Neutralstellung oder darunter -> Stopp
        motor_pwm.duty_cycle = 0
        return 0.0
def set_servo_speed(x_raw):
    if x_raw > DEADZONE:
        speed_pct = ((x_raw - DEADZONE) / (MAX_ADC - DEADZONE)) * 100
        speed_pct = max(0.0, min(100.0, speed_pct))
        servo_dir.value = True
        duty = int((speed_pct / 100) * 65535)
        servo_pwm.duty_cycle = duty
        return speed_pct
    elif x_raw < DEADZONE_INV:
        speed_pct = ((DEADZONE_INV - x_raw) / DEADZONE_INV) * 100
        speed_pct = max(0.0, min(100.0, speed_pct))
        servo_dir.value = False
        duty = int((speed_pct / 100) * 65535)
        servo_pwm.duty_cycle = duty
        return speed_pct
    else:
        servo_pwm.duty_cycle = 0
        return 0.0



# --- MAIN LOOP ---
print(f"[SYSTEM] Server läuft. Warte auf ESP32 an Port {UDP_PORT}...")

try:
    while True:
        # --- TEIL 1: TCP (TELEMETRIE) ---
        if active_conn is None:
            try:
                conn, addr = tcp_server.accept()
                active_conn = conn
                active_conn.setblocking(False)
                print(f"\n[TCP] ESP32 verbunden: {addr}")
            except BlockingIOError:
                pass
        else:
            try:
                data = active_conn.recv(1024)
                if not data:
                    print("\n[TCP] ESP32 getrennt.")
                    active_conn.close()
                    active_conn = None
                else:
                    msg = data.decode('utf-8', errors='ignore').strip()
                    # Wenn ESP was schickt, antworten wir mit Fake-Telemetrie
                    # Damit dein ESP-Display oder Log etwas zum Anzeigen hat
                    active_conn.sendall(b"BATT:3.82\nVEL:20\n")
            except BlockingIOError:
                pass
            except Exception:
                active_conn = None

        # --- TEIL 2: UDP (JOYSTICK & MOTOR) ---
        try:
            data, addr = udp_sock.recvfrom(1024)
            if len(data) >= 5:
                # Entpackt: uint16_t x, uint16_t y, uint8_t mode
                x, y, mode = struct.unpack('<HHB', data[:5])

                # Motor-Geschwindigkeit basierend auf Y aktualisieren
                current_speed = set_motor_speed(y)
                current_rotation = set_servo_speed(x)

                if current_speed > 0:
                    print(f"[DRIVE] Joystick: {y} | Speed: {round(current_speed, 1)}%   ", end="\r")
                else:
                    print("[DRIVE] Neutral (Stopp)                          ", end="\r")
        except socket.timeout:
            pass
        except Exception as e:
            print(f"\n[UDP FEHLER] {e}")

        # Extrem kurze Pause für hohe Reaktionsgeschwindigkeit
        time.sleep(0.001)

except KeyboardInterrupt:
    print("\n[SYSTEM] Beende...")
finally:
    # Motoren sofort ausschalten bei Programmende
    try:
        motor_pwm.duty_cycle = 0
        motor_pwm.deinit()
        motor_dir.deinit()
    except:
        pass
    print("[SYSTEM] Alles sicher abgeschaltet.")