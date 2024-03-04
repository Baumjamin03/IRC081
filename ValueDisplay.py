# ValueDisplay class file
import customtkinter as ctk
from BaseFrame import BaseFrame


class HotizontalValueDisplay(BaseFrame):
    def __init__(self, master, row, col, title, *args, **kwargs):
        super().__init__(master, row, col, title, pady=0, *args, **kwargs)
        self.value = ctk.StringVar()
        self.lblValue = ctk.CTkLabel(self, textvariable=self.value)
        self.lblValue.grid(row=0, column=1, pady=0, sticky="nsew")


class VerticalValueDisplay():
    pass
