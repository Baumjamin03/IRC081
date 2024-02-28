# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:55:21 2024

@author: benj002
"""


# touchscreen_gui_customtkinter.py
import customtkinter as ctk

# Define the custom window dimensions
WIDTH = 800
HEIGHT = 480

PADY = 5
PADX = 5

pressure = "7284"
ionCurrent = "9790"

class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        self.maxsize(WIDTH, HEIGHT)
        
        self.title("IRUI082")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.frameDaq = SubFrame(self)
        self.frameDaq.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.frameDaq.label.configure(text="DAQ")
        self.frameDaq.switch_var = ctk.StringVar(value="off")
        self.frameDaq.switch = ctk.CTkSwitch(self.frameDaq, text="DAQ UP", command=self.switch_event,
                                             variable=self.frameDaq.switch_var, onvalue="on", offvalue="off")
        self.frameDaq.switch.grid(row=1, column=0,)
        
        self.frameAnalogOut = SubFrame(self)
        self.frameAnalogOut.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="nsew")
        self.frameAnalogOut.label.configure(text="Analog Voltage")
        
        self.framePressure = SubFrame(self)
        self.framePressure.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.framePressure.label.configure(text="Pressure")
        
        self.frameSerial = SubFrame(self)
        self.frameSerial.grid(row=1, column=1, padx=PADX, pady=PADY, sticky="nsew")
        self.frameSerial.label.configure(text="LOG or sum, idk")
        
        self.frameVoltages = SubFrame(self)
        self.frameVoltages.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nsew", columnspan=2)
        self.frameVoltages.label.configure(text="IRG080 Voltages")
             
        
    def daqConnect(self):
        print("test")
    
    def getPressure(self):
        return pressure
    
    def getIonCurrent(self):
        return ionCurrent
    
    def switch_event(self):
        print("switch toggled, current value:", self.frameDaq.switch_var.get())

class SubFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.label = ctk.CTkLabel(self)
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="w")
        
        
    
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()