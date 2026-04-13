import socket
import struct
import random
import time

from Comm.inputHandler import inputHandler
from Sensoren import ADC
from Sensoren.ADC import ADC

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

def sendRealValues(batt, vel):
    sendTCP(active_tcp_connection, "BATT", batt)
    sendTCP(active_tcp_connection, "VEL", vel)

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

def udpHandler():
    if active_tcp_connection:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', UDP_PORT))
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if len(data) <= 5:
                    x, y, mode = struct.unpack('<HHB', data[:5])
                    latest_udp_data_x = x
                    latest_udp_data_y = y
                    latest_udp_data_mode = mode
                    print(latest_udp_data_x, latest_udp_data_y, latest_udp_data_mode)
                    inputHandler(latest_udp_data_y)
            except: pass

def connHandler(adc):
    global active_tcp_connection, latest_tcp_msg
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", TCP_PORT))
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        active_tcp_connection = conn
        while True:
            try:
                data = conn.recv(1024)
                if not data: break
                msg = data.decode('utf-8', errors='ignore').strip()
                sendRealValues(adc.get_ampere(0), 0)
            except: break
        active_tcp_connection = None
        conn.close()

