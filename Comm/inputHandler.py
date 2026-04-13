import struct
from Comm import active_tcp_connection
from Motor import motors

def inputHandler(y):
    if active_tcp_connection:
        if y > 1950:
            movement_y = ((y - 1950) / (4096 - 1950)) * 100
            motors.vorwaerts(movement_y)
