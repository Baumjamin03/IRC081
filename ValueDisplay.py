# ValueDisplay class file
import customtkinter as ctk
from GlobalVariables import *
from BaseFrame import BaseFrame


class ValueDisplay(BaseFrame):
    def __init__(self, master, row, col, title, *args, **kwargs):
        super().__init__(master, row, col, title, *args, **kwargs)
        self.value = ctk.StringVar()
        self.lblValue = ctk.CTkLabel(self, textvariable=self.value)
        self.lblValue.grid(row=0, column=1, sticky="nsew")
