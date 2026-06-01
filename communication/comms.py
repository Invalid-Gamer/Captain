import logging
import socket
import struct
import random
import threading
import time
import select

from communication.inputHandler import inputHandler
import globals

latest_tcp_msg = ""
active_tcp_connection = None
TCP_PORT = 9006
UDP_PORT = 9005

def parseUDPData(data): # UDP Daten entpacken
    if len(data) >= 5:
        return struct.unpack('<HHB', data[:5])
    return None


def DecodeTCP(data): # Deprecated
    try:
        return data.decode('utf-8').strip()
    except UnicodeDecodeError:
        return None


def sendTCP(conn, key, value): # rohe Sendefunktion für TCP
    if conn:
        try:
            msg = f"{key}:{value}\n"
            conn.sendall(msg.encode())
            return True
        except Exception as e:
            print(f"Sende-Fehler: {e}")
            return False
    return False


def sendSimulatedValues(conn): #Deprecated
    batt = round(random.uniform(3.3, 4.2), 2)
    vel = random.randint(0, 100)

    s1 = sendTCP(conn, "BATT", batt)
    s2 = sendTCP(conn, "VEL", vel)
    return s1 and s2

def sendRealValues(batt, lenk, ampere, absv, absh): # Sende Sensordaten über TCP
    batt = "BATT:" + str(batt)
    lenk = "LENK:" + str(lenk)
    ampere = "AMPR:" + str(ampere)
    absv = "ABSV:" + str(absv)
    absh = "ABSH:" + str(absh)
    sendTCP(active_tcp_connection, "SDATA", batt)
    sendTCP(active_tcp_connection, "SDATA", lenk)
    sendTCP(active_tcp_connection, "SDATA", ampere)
    sendTCP(active_tcp_connection, "SDATA", absv)
    sendTCP(active_tcp_connection, "SDATA", absh)

def handle_incoming_udp(sock): # UDP Empfangen und verpacken
    global latest_udp_data
    try:
        data, addr = sock.recvfrom(1024)
        result = parseUDPData(data)
        if result:
            latest_udp_data["x"], latest_udp_data["y"], latest_udp_data["mode"] = result
            return latest_udp_data
    except Exception:
        pass
    return None

def tcpHandler(adc,tof): # Thread, der Sensordaten holt und versendet
    t = threading.current_thread()
    while getattr(t, "do_run", True):
        currentVoltage = adc.get_12voltage(1)
        currentLenkung = adc.get_lenkung(2)
        currentAmpere = adc.get_ampere(0)
        currentAbsV = tof.get_mm_vorne()
        currentAbsH = tof.get_mm_hinten()
        logging.debug(f"Sending Voltage: {currentVoltage}")
        logging.debug(f"Sending Lenkung: {currentLenkung}")
        logging.debug(f"Sending Ampere: {currentAmpere}")
        logging.debug(f"Sending Abstand Vorne: {currentAbsV}")
        logging.debug(f"Sending Abstand Hinten: {currentAbsH}")
        sendRealValues(currentVoltage,currentLenkung, currentAmpere, currentAbsV, currentAbsH)
        time.sleep(1)

def udpHandler(adc, motors): # Für modes 1 und 2: Joystick Daten empfangen und verarbeiten
        t = threading.current_thread()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', UDP_PORT))
        sock.settimeout(0.2)
        logging.debug(getattr(t, "do_run", True))
        latest_udp_msg = time.time()
        while getattr(t, "do_run", True):
            try:
                data, addr = sock.recvfrom(1024)
                if len(data) >= 4:
                    latest_udp_msg = time.time()
                    x, y = struct.unpack('<HH', data[:4])
                    latest_udp_data_x = x
                    latest_udp_data_y = y
                    inputHandler(latest_udp_data_x, latest_udp_data_y, motors, adc)
            except socket.timeout:
                pass
            except Exception as e:
                logging.error(f"UDP Fehler: {e}")

            if latest_udp_msg < time.time() - 1:
                motors.stop()
                motors.stoplenkung()

def connHandler(adc, motors,tof): # Thread, Hauptschleife für Kommunikation
    t1 = threading.Thread(target=udpHandler, args=(adc,motors,))
    global active_tcp_connection, latest_tcp_msg
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(("0.0.0.0", TCP_PORT))
    tcp_sock.listen(1)
    tcp_sock.settimeout(1)
    active_tcp_connection = None

    while True:
        try:
            t2 = threading.Thread(target=tcpHandler, args=(adc,tof,))
            try: # Verbindung aufbauen und Timeouts festlegen
                conn, addr = tcp_sock.accept()
                active_tcp_connection = conn
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 2)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
                logging.info(f"Verbunden mit {addr}")
            except socket.timeout:
                continue

            if not (t2.is_alive()):  # Fehler ist bekannt, nicht critical aber Lösung noch nicht gefunden
                t2 = threading.Thread(target=tcpHandler, args=(adc, tof,))
                t2.start()

            while active_tcp_connection:
                try: # Überprüfen ob die Verbindung noch steht
                    readable, _, exceptional = select.select(
                        [active_tcp_connection], [], [active_tcp_connection], 0.5
                    )

                    if exceptional:
                        logging.warning("Verbindung fehlerhaft, trenne...")
                        break
                    if not readable:
                        continue

                    data = active_tcp_connection.recv(1024) # TCP von der Fernbedienung
                    if not data:
                        logging.info("Client Verbindung sauber getrennt.")
                        break

                    recv_buffer += data.decode('utf-8', errors='ignore')

                    while '\n' in recv_buffer:
                        line, recv_buffer = recv_buffer.split('\n', 1)
                        line = line.strip()
                        if not line:
                            continue  # "\r\n"-Fragmente und Leerzeilen überspringen

                        if ':' not in line:
                            logging.debug(f"Nachricht ohne Trenner ignoriert: {repr(line)}")
                            continue

                        key, value = line.split(':', 1)
                        logging.debug(line)

                        if key == "mode":
                            globals.current_mode = int(value)
                            logging.debug(f"Current Mode: {globals.current_mode}")
                        elif key == "conf":
                            logging.warning(f"Config Section not developed!\nConfig Value: {value}")
                        else:
                            logging.debug(f"Command nicht gefunden: {key}:{value}")


                except Exception as e:
                    logging.error(f"Fehler beim Empfangen: {e}")
                    break


            # Ab hier ist die while Schleife vorbei
            logging.info("Client getrennt, räume auf...")
            if active_tcp_connection:
                active_tcp_connection.close()
            active_tcp_connection = None
            if t2.is_alive():
                t2.do_run = False
                t2.join(timeout=5)
                if t2.is_alive():
                    logging.warning("t2 konnte nicht auber beendet werden.")

            motors.stop()
            motors.stoplenkung()

        except Exception as e:
            logging.error(f"Kritischer Fehler: {e}")
            time.sleep(1)