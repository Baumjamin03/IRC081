from Pages.BasePage import *


class SettingsPageClass(BasePageClass):
    def __init__(self,
                 master: any,
                 range_setter: callable):
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frameAnalogue = ctk.CTkFrame(self, fg_color=infBlue, bg_color=infBlue)
        self.frameAnalogue.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.frameControl = ctk.CTkFrame(self, fg_color=infBlue, bg_color=infBlue)
        self.frameControl.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.lblAnalogueOut = ctk.CTkLabel(self.frameAnalogue, text="Analogue Out", text_color="white",
                                           font=("Arial", 18, "bold"), fg_color=infBlue)
        self.lblAnalogueOut.grid(row=0, column=0, columnspan=2, pady=15)

        self.frameRange = ctk.CTkFrame(self.frameAnalogue, fg_color=infBlue, bg_color=infBlue)
        self.frameRange.grid(row=1, column=0, columnspan=2)

        self.frameAnalogue = ctk.CTkFrame(self.frameAnalogue, fg_color=infBlue, bg_color=infBlue)
        self.frameAnalogue.grid(row=2, column=0, columnspan=2)

        self.lblUpper = ctk.CTkLabel(self.frameRange, text="Upper Range: ", text_color="white",
                                     font=("Arial", 14, "bold"), fg_color=infBlue)
        self.lblUpper.grid(row=0, column=1, padx=5)

        self.entryUpper = TouchEntry(self.frameRange, 0, 1)
        self.entryUpper.insert(0, "9E-7")
        self.entryUpper.bind("<Button-1>", lambda event: master.show_numpad(self.entryUpper, "Settings"))
        self.entryUpper.grid(row=1, column=1, padx=5)

        self.lblLower = ctk.CTkLabel(self.frameRange, text="Lower Range: ", text_color="white",
                                     font=("Arial", 14, "bold"), fg_color=infBlue)
        self.lblLower.grid(row=0, column=0, padx=5)

        self.entryLower = TouchEntry(self.frameRange, 1, 1)
        self.entryLower.insert(0, "1E-7")
        self.entryLower.bind("<Button-1>", lambda event: master.show_numpad(self.entryLower, "Settings"))
        self.entryLower.grid(row=1, column=0, padx=5)

        self.entryLower = TouchEntry(self.frameRange, 1, 1)
        self.entryLower.insert(0, "1E-7")
        self.entryLower.bind("<Button-1>", lambda event: master.show_numpad(self.entryLower, "Settings"))

        self.btnSetRange = ctk.CTkButton(self.frameRange, border_color="white", border_width=3, text_color="white",
                                         text="Set Range", height=40, command=range_setter)
        self.btnSetRange.grid(row=2, column=0, columnspan=2, pady=10)

        self.lblOut = ValueDisplay(self.frameAnalogue, "Analogue Out (V):", 0, 0)

        self.frameValues = ctk.CTkFrame(self, fg_color=infBlue, bg_color=infBlue)
        self.frameValues.grid(row=1, column=0, columnspan=2, pady=5)
        self.values = {
            "iFaraday": ValueDisplay(self.frameValues, "Faraday (A):", 0, 0),
            "iCage": ValueDisplay(self.frameValues, "Cage (A):", 0, 1),
            "iEmission": ValueDisplay(self.frameValues, "Emission (A):", 0, 2),
            "iCollector": ValueDisplay(self.frameValues, "Collector (A):", 0, 3)
        }

        self.lblControlGauge = ctk.CTkLabel(self.frameControl, text="Control Gauge", text_color="white",
                                            font=("Arial", 18, "bold"), fg_color=infBlue)
        self.lblControlGauge.grid(row=0, column=0, pady=10, columnspan=2)

        self.lblConnectedControlGauge = ValueDisplay(self.frameControl, "Connected Control Gauge:", 1, 0)

        self.frameControlOn = ctk.CTkFrame(self.frameControl, fg_color=infBlue, bg_color=infBlue)
        self.frameControlOn.grid(row=2, column=0, pady=10, sticky="nsew")
        self.frameControlOn.grid_columnconfigure(0, weight=1)

        self.lblUseControlGauge = ctk.CTkLabel(self.frameControlOn, text="Use Control Gauge", text_color="white",
                                               font=("Arial", 14, "bold"), fg_color=infBlue)
        self.lblUseControlGauge.grid(row=0, column=0, pady=(10, 0))

        self.switchUseControlGauge = ctk.CTkSwitch(self.frameControlOn, text="", fg_color="red", progress_color="green",
                                                   switch_height=50, switch_width=100)
        self.switchUseControlGauge.grid(row=1, column=0, padx=55, pady=(5, 10), sticky="nsew")

        self.lblPressure = ValueDisplay(self.frameControl, "Pressure (mbar):", 3, 0)
