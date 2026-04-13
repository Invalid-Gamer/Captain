import socket
import struct
import random
import time

# Entferne den Import von hier oben!
# import inputHandler  <-- Weg damit

active_tcp_connection = None
TCP_PORT = 9006
UDP_PORT = 9005


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
        except:
            return False
    return False


def sendRealValues(batt, vel):
    global active_tcp_connection
    sendTCP(active_tcp_connection, "BATT", batt)
    sendTCP(active_tcp_connection, "VEL", vel)


def udpHandler():
    import inputHandler  # Import erst HIER aufrufen (Lazy Loading)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('0.0.0.0', UDP_PORT))
    except Exception as e:
        print(f"UDP Bind Error: {e}")
        return

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            result = parseUDPData(data)
            if result:
                x, y, mode = result
                # Direkt den Handler aus dem importierten Modul nutzen
                inputHandler.inputHandler(y)
        except:
            pass


def connHandler(adc):
    global active_tcp_connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", TCP_PORT))
    sock.listen(1)

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

                # Telemetrie
                current_ampere = adc.get_ampere(0)
                sendRealValues(current_ampere, 0)
            except:
                break

        active_tcp_connection = None
        conn.close()