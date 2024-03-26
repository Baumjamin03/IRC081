# Numbpad class file
import customtkinter as ctk
from GlobalVariables import *


class NumbPad(ctk.CTkToplevel):
    def __init__(self, entry, *args, **kwargs):
        """
        Initializes the pop-up numbpad for the touchscreen
        """
        super().__init__(*args, **kwargs)
        self.geometry("300x400")
        self.title(entry.cget("placeholder_text"))
        self.overrideredirect(False)

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

        self.buttonArray.append(ctk.CTkButton(self, text="ENTER", width=100, height=100, border_width=3,
                                              border_color="black", fg_color=infBlue, command=self.fo_sho))
        self.buttonArray[12].grid(row=3, column=2)
        self.buttonArray[12].cget("font").configure(size=25)

        try:
            self.wait_visibility()
            self.attributes('-topmost', 1)

        except Exception as e:
            print(str(e))

    def fo_sho(self):
        self.destroy()


class ButtonNumber(ctk.CTkButton):
    def __init__(self, master, row, col, text, entry, *args, **kwargs):
        """
        Initializes a button for the numbpad
        """
        super().__init__(master=master, text=text, width=100, height=100, border_width=3, border_color="black",
                         fg_color=infBlue, command=lambda: self.button_clicked(entry), *args, **kwargs)
        self.grid(row=row, column=col)
        self.cget("font").configure(size=32, weight="bold")

    def button_clicked(self, entry):
        """
        Adds the pressed button value to the entry
        """
        current_value = entry.get()
        if '.' in current_value and str(self.cget("text")) == '.':
            return

        if current_value == "" and str(self.cget("text")) == '.':
            new_value = '0' + str(self.cget("text"))
        else:
            new_value = current_value + str(self.cget("text"))

        entry.delete(0, ctk.END)
        entry.insert(0, new_value)
