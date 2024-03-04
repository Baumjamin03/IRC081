# ValueDisplay class file
import customtkinter as ctk
from BaseFrame import BaseFrame


class BaseValueFrame(BaseFrame):
    def __init__(self, master, row, col, title, *args, **kwargs):
        super().__init__(master, row, col, title, *args, **kwargs)
        self.value = ctk.IntVar()
        self.lblValue = ctk.CTkLabel(self, textvariable=self.value)
        self.grid_columnconfigure(0, weight=1)


class HorizontalValueDisplay(BaseValueFrame):
    def __init__(self, master, row, col, title, *args, **kwargs):
        super().__init__(master, row, col, title, pady=0, *args, **kwargs)
        self.lblValue.grid(row=0, column=1, pady=0, sticky="nsew")


class VerticalValueDisplay(BaseValueFrame):
    def __init__(self, master, row, col, title, *args, **kwargs):
        super().__init__(master, row, col, title, pady=0, *args, **kwargs)
        self.lblValue.grid(row=1, column=0, pady=0, sticky="nsew")
