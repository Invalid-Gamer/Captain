import time

messungen = []
KAP_AH = 9.0
# Versuch, die verbleibende Akkuladung zu berechnen: Zu ungenau

def get_Bat_Prozent() -> float:
    if not messungen:
        return 100.0
    verbrauchte_ah = abs(sum(messungen)) / 3600
    prozent = (1- verbrauchte_ah / KAP_AH)*100
    return round(max(0.0,min(100,prozent)),2)

def collect_Bat_Prozent(adc) -> None:
    while True:
        messungen.append(adc.get_ampere(0))
        time.sleep(1)

