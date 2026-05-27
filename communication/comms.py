import logging
import socket
import struct
import random
import threading
import time
import select

from communication.inputHandler import inputHandler
import globals
from comps.motors.motors import Motors

latest_tcp_msg = ""
active_tcp_connection = None
TCP_PORT = 9006
UDP_PORT = 9005

def parseUDPData(data):
    if len(data) >= 5:
        return struct.unpack('<HHB', data[:5])
    return None


def DecodeTCP(data):
    try:
        return data.decode('utf-8').strip()
    except UnicodeDecodeError:
        return None


def sendTCP(conn, key, value):
    if conn:
        try:
            msg = f"{key}:{value}\n"
            conn.sendall(msg.encode())
            return True
        except Exception as e:
            print(f"Sende-Fehler: {e}")
            return False
    return False


def sendSimulatedValues(conn):
    batt = round(random.uniform(3.3, 4.2), 2)
    vel = random.randint(0, 100)

    s1 = sendTCP(conn, "BATT", batt)
    s2 = sendTCP(conn, "VEL", vel)
    return s1 and s2

def sendRealValues(batt, lenk):
    sendTCP(active_tcp_connection, "BATT", batt)
    sendTCP(active_tcp_connection, "LENK", lenk)

def handle_incoming_udp(sock):
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

def tcpHandler(adc):
    t = threading.current_thread()
    while getattr(t, "do_run", True):
        currentVoltage = adc.get_12voltage(1)
        currentLenkung = adc.get_lenkung(2)
        logging.debug(f"Sending Voltage: {currentVoltage}")
        logging.debug(f"Sending Lenkung: {currentLenkung}")
        sendRealValues(currentVoltage,currentLenkung)
        time.sleep(1)

def udpHandler(adc, motors):
        t = threading.current_thread()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', UDP_PORT))
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
            except:
                pass
            if (latest_udp_msg < time.time() - 1):
                motors.stop()
                motors.stoplenkung()

def connHandler(adc, motors):
    t1 = threading.Thread(target=udpHandler)
    global active_tcp_connection, latest_tcp_msg
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(("0.0.0.0", TCP_PORT))
    tcp_sock.listen(1)
    tcp_sock.settimeout(1)
    active_tcp_connection = None

    while True:
        try:
            t2 = threading.Thread(target=tcpHandler, args=(adc,))
            try:
                conn, addr = tcp_sock.accept()
                active_tcp_connection = conn
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 2)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
                logging.info(f"Verbunden mit {addr}")
            except socket.timeout:
                continue

            while active_tcp_connection:
                try:
                    readable, _, exceptional = select.select(
                        [active_tcp_connection], [], [active_tcp_connection], 0.5
                    )

                    if exceptional:
                        logging.warning("Verbindung fehlerhaft, trenne...")
                        break

                    if not readable:
                        # Timeout – keine Daten, aber Verbindung noch offen → nächste Iteration
                        continue

                    data = active_tcp_connection.recv(1024)
                    if not data:
                        logging.info("Client Verbindung sauber getrennt.")
                        break
                    msg = data.decode('utf-8', errors='ignore').strip()
                    key, value = msg.split(':')
                    if key == "mode":
                        globals.current_mode = int(value)
                        logging.debug(f"Current Mode: {globals.current_mode}")
                    else:
                        logging.debug(f"Command nicht gefunden: {key}:{value}")
                    logging.debug(msg)

                    if not (t2.is_alive()):
                        t2.start()

                except Exception as e:
                    logging.error(f"Fehler beim Empfangen: {e}")
                    break



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