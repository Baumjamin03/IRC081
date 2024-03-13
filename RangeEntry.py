# RangeEntry class file
from BaseFrame import BaseFrame
from GlobalVariables import *
from TouchEntry import TouchEntry


class RangeEntry(BaseFrame):
    def __init__(self, master, row, col, title, pady=0, padx=PADX, *args, **kwargs):
        super().__init__(master, row, col, title, pady=pady, *args, **kwargs)
        self.entry = TouchEntry(self, 1, 0, title=("Enter " + title))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.lblTitle.grid(columnspan=2)
        self.expEntry = TouchEntry(self, 1, 1, title="e-[ENTER]")
