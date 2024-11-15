import customtkinter as ctk

from GlobalVariables import infBlue


class BasePageClass(ctk.CTkFrame):
    def __init__(self,
                 master: any,
                 **kwargs: any):
        super().__init__(master, fg_color=infBlue, bg_color="white", corner_radius=10, **kwargs)


class TouchEntry(ctk.CTkEntry):
    def __init__(self, master, row, col, pady=10, **kwargs):
        super().__init__(master, height=50, justify="center", **kwargs)
        self.grid(row=row, column=col, pady=pady)


class ValueDisplay(ctk.CTkFrame):
    def __init__(self, master, text, row=0, col=0, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=5, border_color="white", border_width=5, **kwargs)
        self.grid(row=row, column=col, sticky="nsew", pady=5, padx=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.lblName = ctk.CTkLabel(self, text=text, anchor="center", height=15, width=100, corner_radius=5, padx=3,
                                    font=("Arial", 15, "bold"), text_color="black")
        self.lblName.grid(row=0, column=0, sticky="ew", padx=3)
        self.value = ctk.DoubleVar(value=12.34)
        self.lblValue = ctk.CTkLabel(self, textvariable=self.value, anchor="center", height=20, width=100,
                                     text_color="black", corner_radius=5, font=("Arial", 14,))
        self.lblValue.grid(row=1, column=0, sticky="ew", padx=3)


class HorizontalValueDisplay(ValueDisplay):
    def __init__(self, *args, value="", **kwargs):
        super().__init__(*args, **kwargs)
        self.grid(pady=5, padx=5, sticky="ns")
        self.lblValue.grid(row=0, column=1, padx=5)
        self.lblName.configure(anchor="e")
        self.lblValue.configure(anchor="w")
        self.s_value = ctk.StringVar(value=value)
        self.lblValue.configure(textvariable=self.s_value)
