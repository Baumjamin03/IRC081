# SubFrame class file
from BaseFrame import BaseFrame


class SubFrame(BaseFrame):
    def __init__(self, master, row, col, title, **kwargs):
        super().__init__(master, row, col, title, **kwargs)
        self.lblTitle.cget("font").configure(size=20, weight="bold")
        self.lblTitle.grid(columnspan=9)
        self.grid_columnconfigure(len(self.grid_slaves(row=0)), weight=1)
