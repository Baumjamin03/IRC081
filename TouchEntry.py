# TouchEntry class file
import customtkinter as ctk
from NumbPad import NumbPad
from GlobalVariables import *


class TouchEntry(ctk.CTkEntry):
    def __init__(self, master, row, col, title, padx=PADX, pady=PADY, *args, **kwargs):
        super().__init__(master, placeholder_text_color="darkgrey", placeholder_text=title, *args, **kwargs)
        self.grid(row=row, column=col, padx=padx, pady=pady, sticky="nsew")
        self.numPad = None
        self.bind("<Button-1>", lambda event, entry=self: self.entry_clicked(self, event))

    def entry_clicked(self, entry, event):
        entry.delete(0, ctk.END)
        if self.numPad is None or not self.numPad.winfo_exists():
            self.numPad = NumbPad(entry)
        self.numPad.grab_set()
