# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:55:21 2024

@author: benj002
"""

import customtkinter as ctk
from GlobalVariables import *
from BaseFrame import BaseFrame
from ValueDisplay import HorizontalValueDisplay, VerticalValueDisplay
from SubFrame import SubFrame
from TouchEntry import TouchEntry
from RangeEntry import RangeEntry
from IRC081 import IRC081

# Define the custom window dimensions
WIDTH = 800
HEIGHT = 480

# simulation variables
pressure = "7284"
ionCurrent = "9790"
leDAQ = "USB-2408-yeeee"


class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(fg_color="black")

        self.irc081 = IRC081()

        self.title("IRUI082")
        self.geometry(f"{WIDTH}x{HEIGHT}")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.frameDaq = SubFrame(self, 0, 0, "DAQ")
        self.frameDaq.switch_var = ctk.StringVar(value="off")
        self.frameDaq.switch = ctk.CTkSwitch(self.frameDaq, text="DAQ UP", command=self.switch_event,
                                             switch_width=100, switch_height=50,
                                             variable=self.frameDaq.switch_var, onvalue="on", offvalue="off")
        self.frameDaq.switch.grid(row=1, column=0)
        self.frameDaq.label = ctk.CTkLabel(self.frameDaq, text=leDAQ)
        self.frameDaq.label.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.frameDaq.grid(padx=(PADX * 2, PADX), pady=(PADY * 2, PADY))
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

        self.framePressure = SubFrame(self, 1, 0, "Pressure")
        self.framePressure.grid(padx=(PADX * 2, PADX))
        self.framePressure.grid_columnconfigure((0, 1), weight=1)
        self.framePressure.grid_rowconfigure(1, weight=1)
        self.framePressure.barDisplay = VerticalValueDisplay(self.framePressure, 1, 0, "mbar:")
        self.framePressure.torrDisplay = VerticalValueDisplay(self.framePressure, 1, 1, "torr:")

        self.frameEmission = SubFrame(self, 1, 1, "Emission Current")
        self.frameEmission.grid(padx=(PADX, PADX * 2))
        self.frameEmission.entryCurrent = TouchEntry(self.frameEmission, 1, 1, "Enter Emission Current")
        self.frameEmission.btnSet = ctk.CTkButton(self.frameEmission, text="Set Current",
                                                  command=self.set_emission_curr)
        self.frameEmission.btnSet.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.frameEmission.grid_columnconfigure((0, 1), weight=1)
        self.frameEmission.grid_rowconfigure(1, weight=1)

        self.frameVoltages = SubFrame(self, 2, 0, "IRG080 Voltages")
        self.frameVoltages.grid(columnspan=2, padx=PADX * 2, pady=(PADY, PADY * 2))
        self.frameVoltages.grid_columnconfigure((0, 1, 2), weight=1)

        self.frameVoltages.uWehnelt = HorizontalValueDisplay(self.frameVoltages, 1, 0, "WEHNELT:")
        self.frameVoltages.uCage = HorizontalValueDisplay(self.frameVoltages, 2, 0, "CAGE:")
        self.frameVoltages.uDeflector = HorizontalValueDisplay(self.frameVoltages, 1, 1, "DEFLECTOR:")
        self.frameVoltages.uFaraday = HorizontalValueDisplay(self.frameVoltages, 2, 1, "FARADAY:")
        self.frameVoltages.uFilLow = HorizontalValueDisplay(self.frameVoltages, 1, 2, "FIL LOW:")
        self.frameVoltages.uFilHigh = HorizontalValueDisplay(self.frameVoltages, 2, 2, "FIL HIGH:")

    def daq_connect(self):
        print("test")

    def update_pressure(self):
        self.framePressure.barDisplay.value.set(self.irc081.get_pressure_mbar())

    def get_ion_current(self):
        return ionCurrent

    def set_emission_curr(self):
        self.framePressure.pDisplay.value.set(self.frameEmission.entryCurrent.get())

    def switch_event(self):
        print("switch toggled, current value:", self.frameDaq.switch_var.get())

    def update_values(self):
        self.frameVoltages.uFaraday.value.set(self.irc081.get_voltage_faraday())
        self.frameVoltages.uCage.value.set(self.irc081.get_voltage_cage())
        self.frameVoltages.uDeflector.value.set(self.irc081.get_voltage_deflector())
        self.frameVoltages.uWehnelt.value.set(self.irc081.get_voltage_wehnelt())

        self.update_pressure()



        self.after(2000, self.update_values)


if __name__ == "__main__":
    app = MainWindow()
    app.update_values()

    app.mainloop()
