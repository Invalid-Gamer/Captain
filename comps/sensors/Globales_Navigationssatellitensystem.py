#die person die die datei umbenennt wird sterben
import logging

import serial

class pyGPS:
    def __init__(self, port="/dev/ttyACM0", baud=9600):
        try:
            self.ser = serial.Serial(port=port, baudrate=baud)
        except serial.serialutil.SerialException:
            logging.error("Serialer Port für die GPS-Empfänger kann nicht geöffnet werden!")

    def get_raw(self):
        return self.ser.readline().decode("utf-8").strip()

    def get_time(self):
        while True:
            line = self.ser.readline().decode("utf-8").strip()
            if line.startswith("$GPRMC"):
                parts = line.split(",")

                status = parts[2]
                if status == "A":
                    time = parts[1]

                    hours = int(time[0:2])
                    minutes = int(time[2:4])
                    seconds = float(time[4:])

                    sec_int = int(seconds)
                    return f"{hours:02d}:{minutes:02d}:{sec_int:02d}"
                else:
                    return f"00:00:00"

    def get_lat(self):
        while True:
            line = self.ser.readline().decode("utf-8").strip()
            if line.startswith("$GPRMC"):
                parts = line.split(",")

                status = parts[2]
                if status == "A":
                    lat = parts[3]
                    lat_dir = parts[4]

                    degrees = int(lat[:2])
                    minutes_full = float(lat[2:])

                    minutes = int(minutes_full)
                    seconds = (minutes_full-minutes)*60

                    return f"{degrees}° {minutes:02d}' {seconds:05.2f}\" {lat_dir}"
                else:
                    return "000° 00' 00.00\""

    def get_lon(self):
        while True:
            line = self.ser.readline().decode("utf-8").strip()
            if line.startswith("$GPRMC"):
                parts = line.split(",")

                status = parts[2]
                if status == "A":

                    lon = parts[5]
                    lon_dir = parts[6]

                    degrees = int(lon[:3])
                    minutes_full = float(lon[3:])

                    minutes = int(minutes_full)
                    seconds = (minutes_full-minutes)*60

                    return f"{degrees:03d}° {minutes:02d}' {seconds:05.2f}\" {lon_dir}"
                else:
                    return "000° 00' 00.00\""

    def get_speed_kn(self):
        while True:
            line = self.ser.readline().decode("utf-8").strip()
            if line.startswith("$GPRMC"):
                parts = line.split(",")

                status = parts[2]
                if status == "A":
                    return round(float(parts[7]), 2)
                return 0

    def get_speed(self):
        while True:
            line = self.ser.readline().decode("utf-8").strip()
            if line.startswith("$GPRMC"):
                parts = line.split(",")

                status = parts[2]
                if status == "A":
                    return float(parts[7])
                return 0

    def get_speed_kmh(self):
        while True:
            return round((float(self.get_speed()) * 1.852),2)

    def get_speed_ms(self):
        while True:
            return round((float(self.get_speed()) * 0.514444),2)

    def get_course(self):
        while True:
            line = self.ser.readline().decode("utf-8").strip()
            if line.startswith("$GPRMC"):
                parts = line.split(",")

                status = parts[2]
                if status == "A":

                    course = parts[8]
                    if course == "":
                        course = "---"
                    return course
                else:
                    return 0

    def get_date(self):
        while True:
            line = self.ser.readline().decode("utf-8").strip()
            if line.startswith("$GPRMC"):
                parts = line.split(",")
                status = parts[2]
                if status == "A":
                    date = parts[9]
                    return f"{date[0:2]}.{date[2:4]}.{date[4:6]}"
                return "00.00.0000"

