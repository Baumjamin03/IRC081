# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:55:21 2024

@author: benj002
"""

from SubFrame import *
from IRC081 import IRC081

# Define the custom window dimensions
WIDTH = 800
HEIGHT = 480


class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(fg_color="black")

        self.irc081 = IRC081()

        self.windowWidth = WIDTH
        self.windowHeight = HEIGHT

        self.title("IRUI082")
        self.geometry(f"{self.windowWidth}x{self.windowHeight}")

        self.state('normal')

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.frameDaq = DaqFrame(self)

        self.frameAnalogOut = AnalogFrame(self)

        self.frameEmission = EmissionFrame(self)

        self.framePressure = PressureFrame(self)

        self.frameVoltages = VoltagesFrame(self)

    def measurement_loop(self):
        if self.frameDaq.switch_var.get() == "on":
            self.update_values()
            self.after(1000, self.measurement_loop)

    def set_emission_curr(self):
        current = self.frameEmission.entryCurrent.get()
        print("i emission set: " + current)
        self.irc081.set_emission(current)

    def switch_event(self):
        if self.frameDaq.switch_var.get() == "on":
            self.set_emission_curr()
            self.irc081.measurement_start()
            self.measurement_loop()

        else:
            print("measurement end")
            self.irc081.measurement_end()

    def update_values(self):
        self.irc081.refresh_controller_data()

        self.frameVoltages.uDeflector.value.set("{:.3f}".format(self.irc081.get_voltage_deflector()))
        self.frameVoltages.uWehnelt.value.set("{:.3f}".format(self.irc081.get_voltage_wehnelt()))
        self.frameVoltages.uFaraday.value.set("{:.3f}".format(self.irc081.get_voltage_faraday()))
        self.frameVoltages.uCage.value.set("{:.3f}".format(self.irc081.get_voltage_cage()))
        self.frameVoltages.uBias.value.set("{:.3f}".format(self.irc081.get_voltage_bias()))
        self.frameVoltages.iFil.value.set("{:.3f}".format(self.irc081.get_current_filament()))

        self.frameDaq.emissionDisplay.value.set("{:.5e}".format(self.irc081.get_emission_current()))

        self.framePressure.pressure.set("{:.5e}".format(self.irc081.get_pressure_mbar()))


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
