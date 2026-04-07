import time

from sensors import battery_ampere
from sensors import battery_voltage

def main():
    print("===Testmode ===")
    chan0 = battery_ampere.initmcp()
    chan1 = battery_voltage.initmcp()
    while True:
        battery_ampere.readampere(chan0)
        battery_voltage.readvoltage(chan1)
        time.sleep(0.5)




if __name__ == '__main__':
    main()
