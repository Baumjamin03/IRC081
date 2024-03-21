# BaseFrame class file
import customtkinter as ctk
from GlobalVariables import *


class BaseFrame(ctk.CTkFrame):
    def __init__(self, master, row, col, title, pady=PADY, padx=PADX, *args, **kwargs):
        """
        Initializes the base class for frames in the GUI
        """
        super().__init__(master, *args, **kwargs)
        self.configure(fg_color=infBlue)
        self.grid(row=row, column=col, padx=padx, pady=pady, sticky="nsew")
        self.lblTitle = ctk.CTkLabel(self, text=title, text_color=txtColor, anchor="center")
        self.lblTitle.grid(row=0, column=0, padx=padx, pady=pady, sticky="nsew")
        self.lblTitle.cget("font").configure(weight="bold")
