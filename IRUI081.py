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

#simulation variables
pressure = "7284"
ionCurrent = "9790"
leDAQ = "USB-2408-yeeeeeee"

class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        self.maxsize(WIDTH, HEIGHT)
        
        self.title("IRUI082")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        
        self.grid_columnconfigure((0, 1), weight=1)
        
        self.grid_rowconfigure((0, 1), weight=1)
        
        self.frameDaq = SubFrame(self, 0, 0, "DAQ")
        self.frameDaq.switch_var = ctk.StringVar(value="off")
        self.frameDaq.switch = ctk.CTkSwitch(self.frameDaq, text="DAQ UP", command=self.switch_event,
                                             switch_width=100, switch_height=50,
                                             variable=self.frameDaq.switch_var, onvalue="on", offvalue="off")
        self.frameDaq.switch.grid(row=1, column=0,)
        self.frameDaq.label = ctk.CTkLabel(self, text=leDAQ)
        self.frameDaq.label.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nsew")
        
        self.frameAnalogOut = SubFrame(self, 0, 1, "Analog Voltage")
        
        self.framePressure = SubFrame(self, 1, 0, "Pressure")
        
        self.frameSerial = SubFrame(self, 1, 1, "LOG or sum, idk")
        
        self.frameVoltages = SubFrame(self, 2, 0, "IRG080 Voltages")
        self.frameVoltages.grid(columnspan=2)
             
        
    def daqConnect(self):
        print("test")
    
    def getPressure(self):
        return pressure
    
    def getIonCurrent(self):
        return ionCurrent
    
    def switch_event(self):
        print("switch toggled, current value:", self.frameDaq.switch_var.get())

class SubFrame(ctk.CTkFrame):
    def __init__(self, master, row, col, title, **kwargs):
        super().__init__(master, **kwargs)
        self.label = ctk.CTkLabel(self, text=title)
        self.grid(row=row, column=col, padx=PADX, pady=PADY, sticky="nsew")
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="w")
        
        
    
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()