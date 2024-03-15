# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:55:21 2024

@author: benj002
"""

import customtkinter as ctk
from GlobalVariables import *
from ValueDisplay import HorizontalValueDisplay, VerticalValueDisplay
from SubFrame import SubFrame
from TouchEntry import TouchEntry
from RangeEntry import RangeEntry
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

        self.frameDaq = SubFrame(self, 1, 0, "DAQ")
        self.frameDaq.switch_var = ctk.StringVar(value="off")
        self.frameDaq.switch = ctk.CTkSwitch(self.frameDaq, text="Measure", command=self.switch_event,
                                             switch_width=100, switch_height=50,
                                             variable=self.frameDaq.switch_var, onvalue="on", offvalue="off")
        self.frameDaq.switch.grid(row=1, column=0)
        self.frameDaq.switch.cget("font").configure(size=20)
        self.frameDaq.grid(padx=(PADX * 2, PADX))
        self.frameDaq.grid_columnconfigure(0, weight=1)

        self.frameAnalogOut = SubFrame(self, 0, 1, "Analog Voltage")
        self.frameAnalogOut.grid(padx=(PADX, PADX * 2), pady=(PADY * 2, PADY))

        self.frameAnalogOut.entryUpperRange = RangeEntry(self.frameAnalogOut, 1, 1, "Upper Range Limit")
        self.frameAnalogOut.entryLowerRange = RangeEntry(self.frameAnalogOut, 2, 1, "Lower Range Limit")

        self.frameAnalogOut.btnSetRange = ctk.CTkButton(self.frameAnalogOut, text="Set Range")
        self.frameAnalogOut.btnSetRange.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nsew")

        self.frameAnalogOut.grid_columnconfigure((0, 1), weight=1)
        self.frameAnalogOut.grid_rowconfigure((1, 2), weight=1)
        self.frameAnalogOut.frameVoltageDisplay = VerticalValueDisplay(self.frameAnalogOut, 1, 0, "U Out:")

        self.frameEmission = SubFrame(self, 1, 1, "Emission Current")
        self.frameEmission.grid(padx=(PADX, PADX * 2))
        self.frameEmission.entryCurrent = TouchEntry(self.frameEmission, 1, 1, "Enter Emission Current")
        self.frameEmission.btnSet = ctk.CTkButton(self.frameEmission, text="Set Current",
                                                  command=self.set_emission_curr)
        self.frameEmission.btnSet.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.frameEmission.grid_columnconfigure((0, 1), weight=1)
        self.frameEmission.grid_rowconfigure(1, weight=1)
        self.frameEmission.lblUnit = ctk.CTkLabel(self.frameEmission, text="uA")
        self.frameEmission.lblUnit.grid(column=2, row=1, padx=(PADX, PADX * 2))
        self.frameEmission.lblUnit.cget("font").configure(weight="bold", size=20)

        self.framePressure = SubFrame(self, 0, 0, "Pressure")
        self.framePressure.grid(padx=(PADX * 2, PADX), pady=(PADY * 2, PADY))
        self.framePressure.grid_rowconfigure(1, weight=1)
        self.framePressure.grid_columnconfigure(0, weight=1)

        self.framePressure.pressure = ctk.DoubleVar()
        self.framePressure.barDisplay = ctk.CTkLabel(self.framePressure, textvariable=self.framePressure.pressure)
        self.framePressure.barDisplay.grid(columnspan=2)

        self.frameVoltages = SubFrame(self, 2, 0, "IRG080 Voltages")
        self.frameVoltages.grid(columnspan=2, padx=PADX * 2, pady=(PADY, PADY * 2))
        self.frameVoltages.grid_columnconfigure((0, 1, 2), weight=1)

        self.frameVoltages.uWehnelt = HorizontalValueDisplay(self.frameVoltages, 1, 0, "WEHNELT:")
        self.frameVoltages.uCage = HorizontalValueDisplay(self.frameVoltages, 2, 0, "CAGE:")
        self.frameVoltages.uDeflector = HorizontalValueDisplay(self.frameVoltages, 1, 1, "DEFLECTOR:")
        self.frameVoltages.uFaraday = HorizontalValueDisplay(self.frameVoltages, 2, 1, "FARADAY:")
        self.frameVoltages.uBias = HorizontalValueDisplay(self.frameVoltages, 1, 2, "BIAS:")
        self.frameVoltages.iFil = HorizontalValueDisplay(self.frameVoltages, 2, 2, "FIL CURRENT:")

    def measurement_loop(self):

        if self.frameDaq.switch_var.get() == "on":
            self.update_values()

            self.after(1000, self.measurement_loop)

    def update_pressure(self):
        self.framePressure.pressure.set(self.irc081.get_pressure_mbar())

    def set_emission_curr(self):
        current = self.frameEmission.entryCurrent.get()
        print("i emission set: " + current)
        self.irc081.set_emission_curr(current)

    def switch_event(self):
        if self.frameDaq.switch_var.get() == "on":
            self.irc081.measurement_start()
            self.measurement_loop()
            self.set_emission_curr()
        else:
            print("measurement end")

            self.irc081.measurement_end()

    def update_values(self):
        self.frameVoltages.uDeflector.value.set(self.irc081.get_voltage_deflector())
        self.frameVoltages.uWehnelt.value.set(self.irc081.get_voltage_wehnelt())
        self.frameVoltages.uFaraday.value.set(self.irc081.get_voltage_faraday())
        self.frameVoltages.uCage.value.set(self.irc081.get_voltage_cage())
        self.frameVoltages.uBias.value.set("{:.3f}".format(self.irc081.get_voltage_bias()))
        self.frameVoltages.iFil.value.set(self.irc081.get_current_filament())

        self.update_pressure()


if __name__ == "__main__":
    app = MainWindow()

    app.mainloop()
