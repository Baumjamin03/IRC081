# Numbpad class file
import customtkinter as ctk
from GlobalVariables import *


class NumbPad(ctk.CTkToplevel):
    def __init__(self, entry, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("300x400")
        self.resizable(False, False)

        self.btn0 = ButtonNumber(self, 3, 1, "0", entry)
        self.btn1 = ButtonNumber(self, 2, 0, "1", entry)
        self.btn2 = ButtonNumber(self, 2, 1, "2", entry)
        self.btn3 = ButtonNumber(self, 2, 2, "3", entry)
        self.btn4 = ButtonNumber(self, 1, 0, "4", entry)
        self.btn5 = ButtonNumber(self, 1, 1, "5", entry)
        self.btn6 = ButtonNumber(self, 1, 2, "6", entry)
        self.btn7 = ButtonNumber(self, 0, 0, "7", entry)
        self.btn8 = ButtonNumber(self, 0, 1, "8", entry)
        self.btn9 = ButtonNumber(self, 0, 2, "9", entry)
        self.btnDot = ButtonNumber(self, 3, 0, ".", entry)

        self.btnEnter = ctk.CTkButton(self, text="fo\nsho", width=100, height=100, border_width=3, border_color="black",
                                      fg_color=infBlue, command=self.fo_sho)
        self.btnEnter.grid(row=3, column=2)
        self.btnEnter.cget("font").configure(size=29)

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


if __name__ == "__main__":
    app = NumbPad()
    app.mainloop()
