# ValueDisplay class file
import customtkinter as ctk
from BaseFrame import BaseFrame


class BaseValueFrame(BaseFrame):
    def __init__(self, master, row, col, title, *args, **kwargs):
        """
        Initializes the base class for value displays
        """
        super().__init__(master, row, col, title, *args, **kwargs)
        self.value = ctk.DoubleVar()
        self.lblValue = ctk.CTkLabel(self, textvariable=self.value, anchor="center")


class HorizontalValueDisplay(BaseValueFrame):
    def __init__(self, master, row, col, title, *args, **kwargs):
        """
        Initializes horizontal value displays
        """
        super().__init__(master, row, col, title, pady=0, *args, **kwargs)
        self.lblValue.grid(row=0, column=1, sticky="nsew")
        self.lblValue.configure(anchor="w")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.lblTitle.configure(pady=0, padx=0, width=82)


class VerticalValueDisplay(BaseValueFrame):
    def __init__(self, master, row, col, title, *args, **kwargs):
        """
        Initializes vertical value Displays
        """
        super().__init__(master, row, col, title, pady=0, *args, **kwargs)
        self.lblValue.grid(row=1, column=0)
        self.lblTitle.cget("font").configure(size=17)
        self.lblValue.cget("font").configure(size=15)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        self.check_var = ctk.BooleanVar(value=True)
        self.autoRange = ctk.CTkCheckBox(self, text="Autorange", variable=self.check_var, onvalue=True, offvalue=False)
        self.autoRange.grid(row=0, column=1, sticky="nsew", rowspan=2)
