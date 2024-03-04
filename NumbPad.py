# Numbpad class file
import customtkinter as ctk
from GlobalVariables import *


class NumbPad(ctk.CTkToplevel):
    def __init__(self, entry, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("300x400")
        self.title(entry.cget("placeholder_text"))

        self.buttonArray = [12]
        row = 0
        col = 0
        for i in range(1, 10):
            if col == 3:
                col = 0
                row += 1
            self.buttonArray.append(ButtonNumber(self, row, col, str(i), entry))
            col += 1

        self.buttonArray.append(ButtonNumber(self, 3, 1, "0", entry))

        self.buttonArray.append(ButtonNumber(self, 3, 0, ".", entry))

        self.buttonArray.append(ctk.CTkButton(self, text="fo\nsho", width=100, height=100, border_width=3,
                                              border_color="black", fg_color=infBlue, command=self.fo_sho))
        self.buttonArray[12].grid(row=3, column=2)
        self.buttonArray[12].cget("font").configure(size=29)

    def fo_sho(self):
        self.destroy()


class ButtonNumber(ctk.CTkButton):
    def __init__(self, master, row, col, text, entry, *args, **kwargs):
        super().__init__(master=master, text=text, width=100, height=100, border_width=3, border_color="black",
                         fg_color=infBlue, command=lambda: self.button_clicked(entry), *args, **kwargs)
        self.grid(row=row, column=col)
        self.cget("font").configure(size=29, weight="bold")

    def button_clicked(self, entry):
        current_value = entry.get()
        new_value = current_value + str(self.cget("text"))
        entry.delete(0, ctk.END)
        entry.insert(0, new_value)
