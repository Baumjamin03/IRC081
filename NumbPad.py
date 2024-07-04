# Numbpad class file
import customtkinter as ctk
from GlobalVariables import *


class NumbPad(ctk.CTkToplevel):
    def __init__(self, entry, *args, **kwargs):
        """
        Initializes the pop-up numbpad for the touchscreen
        """
        super().__init__(*args, **kwargs)
        self.title(entry.cget("placeholder_text"))
        self.overrideredirect(False)

        self.buttonArray = [13]
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

        self.buttonArray.append(ctk.CTkButton(self, text="DEL", border_width=3, width=120, height=120,
                                              border_color="black", fg_color=infBlue,
                                              command=lambda: self.backspace(entry)))
        self.buttonArray[12].grid(row=3, column=2, sticky="nsew")
        self.buttonArray[12].cget("font").configure(size=25)

        self.buttonArray.append(ctk.CTkButton(self, text="ENTER", border_width=3, width=120, height=480,
                                              border_color="black", fg_color=infBlue, command=self.exit))
        self.buttonArray[13].grid(row=0, column=3, rowspan=4, sticky="nsew")
        self.buttonArray[13].cget("font").configure(size=25)

        self.value = ctk.StringVar()
        self.lblInput = ctk.CTkLabel(self, textvariable=self.value, fg_color="lightgrey", width=150, corner_radius=5)
        self.lblInput.grid(row=0, column=4, rowspan=4, sticky="nsew")
        self.grid_columnconfigure(4, weight=1)
        self.lblInput.cget("font").configure(size=35)

        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        try:
            self.wait_visibility()
            self.attributes('-topmost', 1)
        except Exception as e:
            print(str(e))

    def exit(self):
        self.destroy()

    def backspace(self, entry):
        current_value = entry.get()

        new_value = current_value[:-1]
        entry.delete(0, ctk.END)
        entry.insert(0, new_value)
        entry.numPad.value.set(new_value)


class ButtonNumber(ctk.CTkButton):
    def __init__(self, master, row, col, text, entry, *args, **kwargs):
        """
        Initializes a button for the numbpad
        """
        super().__init__(master=master, text=text, border_width=3, border_color="black", width=120, height=120,
                         fg_color=infBlue, command=lambda: self.button_clicked(entry), *args, **kwargs)
        self.grid(row=row, column=col, sticky="nsew")
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
        entry.numPad.value.set(new_value)
