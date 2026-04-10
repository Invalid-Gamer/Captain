import socket
import struct
import random
import time

latest_udp_data = {"x": 0, "y": 0, "mode": 0}
latest_tcp_msg = ""
active_tcp_connection = None

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
            conn.sendall(msg.encode('utf-8'))
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


def tcp_server_step(sock):
    global active_tcp_connection, latest_tcp_msg

    if active_tcp_connection is None:
        sock.settimeout(1.0)
        try:
            conn, addr = sock.accept()
            active_tcp_connection = conn
            print(f"ESP32 verbunden: {addr[0]}")
        except socket.timeout:
            return

    try:
        active_tcp_connection.settimeout(0.1)
        data = active_tcp_connection.recv(1024)

        if not data:
            print("ESP32 hat die Verbindung getrennt.")
            active_tcp_connection.close()
            active_tcp_connection = None
            return

        msg = DecodeTCP(data)
        if msg:
            latest_tcp_msg = msg
            if "mode" in msg.lower():
                print(f"Spezial-Info vom ESP: {msg}")
            sendSimulatedValues(active_tcp_connection)

    except socket.timeout:
        pass
    except Exception as e:
        print(f"TCP Fehler: {e}")
        active_tcp_connection.close()
        active_tcp_connection = None