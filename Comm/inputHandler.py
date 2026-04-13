from Motor.motors import vorwaerts
import Comm  # Importiert das ganze Modul

def inputHandler(y):
    # Prüfe die Variable direkt im Comm-Modul (keine lokale Kopie!)
    if Comm.active_tcp_connection is not None:
        if y > 1950:
            # Berechnung des Prozentwerts (0-100)
            movement_y = ((y - 1950) / (4095 - 1950)) * 100
            vorwaerts(movement_y)
        else:
            # Motor stoppen, wenn Stick in Neutralstellung
            vorwaerts(0)