# Backend File for IRC081 raspi extension
from mccDAQ.usb_2400 import *


class IRC081(usb_2408_2AO):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except OSError as e:
            print("no, " + str(e.strerror))
            return
        print("daq ume")

    def set_emission_curr(self, current):
        pass

    def set_analog_range(self):
        pass

    def get_pressure_mbar(self):
        pass

    def get_pressure_torr(self):
        pass

    def get_voltage_wehnelt(self):
        pass

    def get_voltage_deflector(self):
        pass

    def get_voltage_cage(self):
        pass

    def get_voltage_faraday(self):
        pass

    def get_voltage_fillow(self):
        pass

    def get_voltage_filhigh(self):
        pass


if __name__ == "__main__":
    irc081 = IRC081()
