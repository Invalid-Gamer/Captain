from Motor.motors import vorwaerts
import Comm

def inputHandler(y):
    # Wir prüfen direkt den Status in Comm
    if Comm.active_tcp_connection is not None:
        if y > 1950:
            movement_y = ((y - 1950) / (4095 - 1950)) * 100
            vorwaerts(movement_y)
        else:
            vorwaerts(0)