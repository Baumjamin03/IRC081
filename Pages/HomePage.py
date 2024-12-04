from Pages.BasePage import *
from Pages.SettingsPage import TouchEntry


class HomePageClass(BasePageClass):
    def __init__(self,
                 master: any,
                 sw_event: callable,
                 emission_setter: callable):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.vFrame = ctk.CTkFrame(self, fg_color=infBlue)
        self.vFrame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10), columnspan=2)

        self.vFrame.grid_rowconfigure(0, weight=1)
        self.vFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.Voltages = {
            "Bias": ValueDisplay(self.vFrame, "Bias (V):", 0, 0),
            "Wehnelt": ValueDisplay(self.vFrame, "Wehnelt (V):", 0, 1),
            "Faraday": ValueDisplay(self.vFrame, "Faraday (V):", 0, 2),
            "Cage": ValueDisplay(self.vFrame, "Cage (V):", 0, 3),
            "Deflector": ValueDisplay(self.vFrame, "Deflector (V):", 0, 4),
            "Filament": ValueDisplay(self.vFrame, "Filament (A):", 0, 5)
        }

        self.emFrame = ctk.CTkFrame(self, fg_color=infBlue)
        self.emFrame.grid(row=0, column=0)

        self.emOn = StartButton(self.emFrame, text="", corner_radius=30, height=60, width=60, border_width=5,
                                border_color="white", fg_color="#BBD396", command=sw_event, hover=False)
        self.emOn.grid(row=0, column=0)

        self.lblEmission = ctk.CTkLabel(self.emFrame, text="Emission in uA:", font=("Arial", 18, "bold"),
                                        text_color="white")
        self.lblEmission.grid(row=1, column=0, pady=(10, 0))

        self.entryEmission = TouchEntry(self.emFrame, 2, 0, font=("Arial", 18, "normal"))
        self.entryEmission.insert(0, "30")
        self.entryEmission.bind("<Button-1>", lambda event: master.show_numpad(self.entryEmission, "Home"))
        self.entryEmission.grid(sticky="ew")

        self.btnEmission = ctk.CTkButton(self.emFrame, border_color="white", border_width=3, text_color="white",
                                         text="Set Emission",
                                         height=40, command=emission_setter)
        self.btnEmission.grid(row=3, column=0, pady=5)

        self.pressFrame = ctk.CTkFrame(self, fg_color="white", corner_radius=10, width=450)
        self.pressFrame.grid(row=0, column=1, sticky="nsew", pady=30, padx=30)
        self.pressFrame.grid_columnconfigure(0, weight=1)
        self.pressFrame.grid_rowconfigure(0, weight=1)
        self.pressFrame.grid_propagate(False)

        self.pressure = ctk.DoubleVar(value=1.03083e-5)
        self.lblPressure = ctk.CTkLabel(self.pressFrame, textvariable=self.pressure, font=("Arial", 64, "bold"),
                                        anchor="center", text_color="black")
        self.lblPressure.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)

        self.transmissionFrame = ctk.CTkFrame(self.pressFrame, fg_color="white")
        self.transmissionFrame.grid(row=1, column=0, sticky="ns", pady=10)
        self.transmission = ctk.DoubleVar(value=98.55)
        ctk.CTkLabel(self.transmissionFrame, font=("Arial", 36, "bold"), text_color="black",
                     text="Transmission: ", fg_color="white", anchor="e").grid(row=0, column=0, padx=2)

        self.lblTransmission = ctk.CTkLabel(self.transmissionFrame, textvariable=self.transmission,
                                            font=("Arial", 36, "bold"),
                                            anchor="center", text_color="black")
        self.lblTransmission.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(self.transmissionFrame, font=("Arial", 36, "bold"), text_color="black",
                     text="%", anchor="w", fg_color="white").grid(row=0, column=2, sticky="nsew")


class StartButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
