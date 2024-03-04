# RangeEntry class file
from BaseFrame import BaseFrame
from GlobalVariables import *
from TouchEntry import TouchEntry


class RangeEntry(BaseFrame):
    def __init__(self, master, row, col, title, pady=PADY, padx=PADX, *args, **kwargs):
        super().__init__(master, row, col, title, pady=pady, padx=padx, *args, **kwargs)
        self.entry = TouchEntry(self, 1, 0, placeholder_text=("Enter " + title))
        self.grid_rowconfigure(1, weight=1)

