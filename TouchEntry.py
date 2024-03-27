# TouchEntry class file
import customtkinter as ctk
from NumbPad import NumbPad
from GlobalVariables import *


class TouchEntry(ctk.CTkEntry):
    def __init__(self, master, row, col, title, padx=PADX, pady=PADY, *args, **kwargs):
        """
        Initializes entries with a popup touchpad
        """
        super().__init__(master, placeholder_text_color="darkgrey", placeholder_text=title, *args, **kwargs)
        self.grid(row=row, column=col, padx=padx, pady=pady, sticky="nsew")
        self.numPad = None
        self.bind("<Button-1>", lambda entry=self: self.entry_clicked(self))

    def entry_clicked(self, entry):
        """
        Event handler, activates on click/touch of the entry and generates a numbpad
        """
        entry.delete(0, ctk.END)
        if self.numPad:
            self.numPad.destroy()
        self.numPad = NumbPad(entry)
        self.after(150, lambda: self.numPad.wm_attributes('-fullscreen', 'true'))
