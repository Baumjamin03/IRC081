# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:55:21 2024

@author: benj002
"""

import customtkinter as ctk
from customtkinter import CTkLabel

# Define the custom window dimensions
WIDTH = 800
HEIGHT = 480

# Default padding
PADY = 5
PADX = 5

# simulation variables
pressure = "7284"
ionCurrent = "9790"
leDAQ = "USB-2408-yeeee"

# color variables
infBlue = "#1f457a"
txtColor = "lightgrey"


class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        self.maxsize(WIDTH, HEIGHT)
        self.configure(fg_color="black")

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
        
        self.frameAnalogOut = SubFrame(self, 0, 1, "Analog Voltage")
        
        self.framePressure = SubFrame(self, 1, 0, "Pressure")
        self.framePressure.pressure = ctk.StringVar()
        self.framePressure.pDisplay = ValueDisplay(self.framePressure, 1, 0, "pressure")
        
        self.frameEmission = SubFrame(self, 1, 1, "Emission Current")
        self.frameEmission.entryCurrent = ctk.CTkEntry(self.frameEmission, placeholder_text="enter Emission Current",
                                                       placeholder_text_color="darkgrey")
        self.frameEmission.entryCurrent.grid(row=1, column=1, padx=PADX, pady=PADY, sticky="nsew")
        self.frameEmission.btnSet = ctk.CTkButton(self.frameEmission, text="Set Current", command=self.setEmissionCurr)
        self.frameEmission.btnSet.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.frameEmission.grid_columnconfigure((0, 1), weight=1)
        
        self.frameVoltages = SubFrame(self, 2, 0, "IRG080 Voltages")
        self.frameVoltages.grid(columnspan=2)
        self.frameVoltages.grid_columnconfigure((0, 1, 2), weight=1)

        self.frameVoltages.uWehnelt = ValueDisplay(self.frameVoltages, 1, 0, "WEHNELT:")
        self.frameVoltages.uCage = ValueDisplay(self.frameVoltages, 2, 0, "CAGE:")
        self.frameVoltages.uDeflector = ValueDisplay(self.frameVoltages, 1, 1, "DEFLECTOR:")
        self.frameVoltages.uFaraday = ValueDisplay(self.frameVoltages, 2, 1, "FARADAY:")
        self.frameVoltages.uFilLow = ValueDisplay(self.frameVoltages, 1, 2, "FIL LOW:")
        self.frameVoltages.uFilHigh = ValueDisplay(self.frameVoltages, 2, 2, "FIL HIGH:")


    def daqConnect(self):
        print("test")
    
    def getPressure(self):
        return pressure
    
    def getIonCurrent(self):
        return ionCurrent

    def setEmissionCurr(self):
        self.framePressure.pDisplay.value.set(self.frameEmission.entryCurrent.get())
    
    def switch_event(self):
        print("switch toggled, current value:", self.frameDaq.switch_var.get())


class BaseFrame(ctk.CTkFrame):
    def __init__(self, master, row, col, title, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=infBlue)
        self.grid(row=row, column=col, padx=PADX, pady=PADY, sticky="nsew")
        self.lblTitle = ctk.CTkLabel(self, text=title, text_color=txtColor, anchor="center", corner_radius=5)
        self.lblTitle.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nsew")

class SubFrame(BaseFrame):
    def __init__(self, master, row, col, title, **kwargs):
        super().__init__(master, row, col, title, **kwargs)
        self.lblTitle.cget("font").configure(size=20, weight="bold")
        self.lblTitle.grid(columnspan=9)
        self.grid_columnconfigure(len(self.grid_slaves(row=0)), weight=1)


class ValueDisplay(BaseFrame):
    def __init__(self, master, row, col, title, **kwargs):
        super().__init__(master, row, col, title, **kwargs)
        self.value = ctk.StringVar()
        self.lblValue = ctk.CTkLabel(self, textvariable=self.value)
        self.lblValue.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="nsew")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()