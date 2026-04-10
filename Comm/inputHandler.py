import struct

from Comm.Comm import active_tcp_connection, latest_udp_data_y
from Motor.motors import vorwaerts

def inputHandler():
    if active_tcp_connection:
        if latest_udp_data_y > 1950:
            movement_y = ((latest_udp_data_y - 1950) / (4096 - 1950)) * 100
            vorwaerts(movement_y)
