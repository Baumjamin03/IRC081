# SubFrame class file
from ValueDisplay import *
from TouchEntry import TouchEntry
from RangeEntry import RangeEntry
from GlobalVariables import *


class SubFrame(BaseFrame):
    def __init__(self, master, row, col, title, title_size=20, **kwargs):
        super().__init__(master, row, col, title, **kwargs)
        self.lblTitle.cget("font").configure(size=title_size)
        self.lblTitle.grid(columnspan=9)
        self.grid_columnconfigure(len(self.grid_slaves(row=0)), weight=1)


class VoltagesFrame(SubFrame):
    def __init__(self, master):
        super().__init__(master, 2, 0, "IRG080 Voltages")
        self.grid(columnspan=2, padx=PADX * 2, pady=(PADY, PADY * 2))
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.uWehnelt = HorizontalValueDisplay(self, 1, 0, "WEHNELT:")
        self.uCage = HorizontalValueDisplay(self, 2, 0, "CAGE:")
        self.uDeflector = HorizontalValueDisplay(self, 1, 1, "DEFLECTOR:")
        self.uFaraday = HorizontalValueDisplay(self, 2, 1, "FARADAY:")
        self.uBias = HorizontalValueDisplay(self, 1, 2, "BIAS:")
        self.iFil = HorizontalValueDisplay(self, 2, 2, "FIL CURR:")


class PressureFrame(SubFrame):
    def __init__(self, master):
        super().__init__(master, 0, 0, "Pressure")
        self.grid(padx=(PADX * 2, PADX), pady=(PADY * 2, PADY))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.pressure = ctk.DoubleVar()
        self.barDisplay = ctk.CTkLabel(self, text_color="white", textvariable=self.pressure)
        self.barDisplay.grid(columnspan=2)
        self.barDisplay.cget("font").configure(size=30)


class EmissionFrame(SubFrame):
    def __init__(self, master):
        super().__init__(master, 1, 1, "Emission Current")
        self.grid(padx=(PADX, PADX * 2))
        self.entryCurrent = TouchEntry(self, 1, 1, "Enter Emission Current")
        self.btnSet = ctk.CTkButton(self, text="Set Current", command=master.set_emission_curr)
        self.btnSet.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.lblUnit = ctk.CTkLabel(self, text="uA")
        self.lblUnit.grid(column=2, row=1, padx=(PADX, PADX * 2))
        self.lblUnit.cget("font").configure(weight="bold", size=20)


class DaqFrame(SubFrame):
    def __init__(self, master):
        super().__init__(master, 1, 0, "DAQ")
        self.switch_var = ctk.StringVar(value="off")
        self.switch = ctk.CTkSwitch(self, text="Measure", command=master.switch_event, switch_width=100,
                                    switch_height=50, variable=self.switch_var, onvalue="on", offvalue="off")
        self.switch.grid(row=1, column=0)
        self.switch.cget("font").configure(size=20)
        self.emissionDisplay = HorizontalValueDisplay(self, 2, 0, "Emission: ")
        self.emissionDisplay.grid(sticky="nsew")

        self.grid(padx=(PADX * 2, PADX))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)


class AnalogFrame(SubFrame):
    def __init__(self, master):
        super().__init__(master, 0, 1, "Analog Out")
        self.grid(padx=(PADX, PADX * 2), pady=(PADY * 2, PADY))
        self.entryUpperRange = RangeEntry(self, 1, 1, "Upper Range Limit")
        self.entryLowerRange = RangeEntry(self, 2, 1, "Lower Range Limit")
        self.btnSetRange = ctk.CTkButton(self, text="Set Range", command=master.set_range)
        self.btnSetRange.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((1, 2), weight=1)
        self.frameVoltageDisplay = VerticalValueDisplay(self, 1, 0, "U Out:")
