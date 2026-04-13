import socket
import struct
import random
import time
import threading

# Import erst hier, um zirkuläre Importe zu vermeiden
import inputHandler

active_tcp_connection = None
TCP_PORT = 9006
UDP_PORT = 9005

# Globale Daten für UDP
latest_udp_data_x = 2048
latest_udp_data_y = 2048
latest_udp_data_mode = 0


def parseUDPData(data):
    if len(data) >= 5:
        return struct.unpack('<HHB', data[:5])
    return None


def sendTCP(conn, key, value):
    if conn:
        try:
            msg = f"{key}:{value}\n"
            conn.sendall(msg.encode())
            return True
        except Exception:
            return False
    return False


def sendRealValues(batt, vel):
    global active_tcp_connection
    if active_tcp_connection:
        sendTCP(active_tcp_connection, "BATT", batt)
        sendTCP(active_tcp_connection, "VEL", vel)


def udpHandler():
    global latest_udp_data_x, latest_udp_data_y, latest_udp_data_mode
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', UDP_PORT))
    print(f"UDP Listener aktiv auf {UDP_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            result = parseUDPData(data)
            if result:
                x, y, mode = result
                latest_udp_data_x, latest_udp_data_y, latest_udp_data_mode = x, y, mode
                # Aufruf des Handlers
                inputHandler.inputHandler(y)
        except Exception:
            pass


def connHandler(adc):
    global active_tcp_connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", TCP_PORT))
    sock.listen(1)
    print(f"TCP Server wartet auf Port {TCP_PORT}")

    while True:
        conn, addr = sock.accept()
        active_tcp_connection = conn
        print(f"ESP32 verbunden: {addr}")
        conn.settimeout(0.2)

        while True:
            try:
                try:
                    data = conn.recv(1024)
                    if not data: break
                    msg = data.decode('utf-8', errors='ignore').strip()
                    if msg: print(f"Vom ESP: {msg}")
                except socket.timeout:
                    pass

                # Telemetrie senden
                current_ampere = adc.get_ampere(0)
                sendRealValues(current_ampere, 0)
                time.sleep(0.05)  # CPU entlasten

            except Exception:
                break

        conn.close()
        active_tcp_connection = None
        print("Verbindung geschlossen.")