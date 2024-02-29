# BaseFrame class file
import customtkinter as ctk
from GlobalVariables import *


class BaseFrame(ctk.CTkFrame):
    def __init__(self, master, row, col, title, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=infBlue)
        self.grid(row=row, column=col, padx=PADX, pady=PADY, sticky="nsew")
        self.lblTitle = ctk.CTkLabel(self, text=title, text_color=txtColor, anchor="center", corner_radius=5)
        self.lblTitle.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nsew")
