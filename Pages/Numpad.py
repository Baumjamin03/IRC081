import customtkinter as ctk
from _decimal import Decimal, DecimalException

from Pages.BasePage import BasePageClass


class NumpadPageClass(BasePageClass):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.page_manager = master
        self.target_entry = None
        self.original_value = None
        self.og_page = None

        # Configure grid weights for main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Entry row
        self.grid_rowconfigure(1, weight=1)  # Numpad row

        # Entry display
        self.display = ctk.CTkEntry(self, height=40, font=("Arial", 20))
        self.display.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        # Numpad frame
        self.numpad = NumericKeypad(self, entry_widget=self.display)
        self.numpad.grid(row=1, column=0, padx=10, pady=5)

        # Buttons frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Cancel and Confirm buttons
        self.cancel_btn = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self.cancel,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.cancel_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.confirm_btn = ctk.CTkButton(
            self.button_frame,
            text="Confirm",
            command=self.confirm,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.confirm_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew", rowspan=2)

    def show(self,
             entry_widget,
             og_page_name) -> None:
        """Prepare and show the numpad page"""
        self.target_entry = entry_widget
        self.og_page = og_page_name
        self.original_value = entry_widget.get()
        self.display.delete(0, 'end')
        self.display.insert(0, self.original_value)
        self.page_manager.show_page("Numpad")
        self.display.focus()

    def confirm(self) -> None:
        """Confirm the entered value and return to previous page"""
        new_value = self.display.get()
        try:
            Decimal(new_value)
        except DecimalException as ex:
            print(ex)
            return

        if self.target_entry:
            self.target_entry.delete(0, 'end')
            self.target_entry.insert(0, self.display.get())
        self.cleanup()

    def cancel(self) -> None:
        """Cancel the entry and return to previous page"""
        if self.target_entry and self.original_value is not None:
            self.target_entry.delete(0, 'end')
            self.target_entry.insert(0, self.original_value)
        self.cleanup()

    def cleanup(self) -> None:
        """Reset the numpad state"""
        self.target_entry = None
        self.original_value = None
        self.display.delete(0, 'end')
        self.page_manager.show_page(self.og_page)
        self.og_page = None

    def on_page_leave(self) -> None:
        """Called when switching away from numpad page"""
        if self.target_entry:
            self.cancel()


class NumericKeypad(ctk.CTkFrame):
    def __init__(self,
                 master: NumpadPageClass,
                 entry_widget: ctk.CTkEntry = None,
                 **kwargs):
        super().__init__(master, **kwargs)
        self.entry_widget = entry_widget
        self.master = master

        # Configure grid weights
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)

        # Button styling
        btn_font = ("Arial", 18)
        btn_color = "#3B3B3B"
        btn_hover_color = "#4D4D4D"
        btn_width = 60
        btn_height = 60

        # Button layout
        buttons = [
            ['1', '2', '3', 'E'],
            ['4', '5', '6', '⌫'],
            ['7', '8', '9', '↓'],
            ['-', '0', '.', None]
        ]

        # Create buttons
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                if text is not None:
                    btn = ctk.CTkButton(
                        self,
                        text=text,
                        font=btn_font,
                        width=btn_width,
                        height=btn_height,
                        fg_color=btn_color,
                        hover_color=btn_hover_color,
                        command=lambda t=text: self.button_click(t)
                    )
                    btn.grid(row=i, column=j, padx=2, pady=2, sticky="nsew")
                    if text == '↓':
                        btn.grid(rowspan=2)

    def is_valid_number(self, value: str) -> bool:
        """Check if the resulting string would be a valid positive number (including zero)"""
        try:

            # Don't allow negative signs at all
            if '-' in value:
                if 'E' in value:
                    for s in value.split('E'):
                        if s.count('-') > 1:
                            return False
                elif value.count('-') > 1:
                    return False

            # Check for valid scientific notation
            if 'E' in value:
                if value.count('E') > 1:
                    return False

            for s in value.split('E'):
                if s.count('.') > 1:
                    return False

            return True
        except ValueError as er:
            print(er)
            return False

    def button_click(self, value) -> None:
        if not self.entry_widget:
            return

        current = self.entry_widget.get()

        if value == '⌫':
            new_value = current[:-1]
        elif value == '↓':
            self.master.confirm()
            return
        else:
            new_value = current + value

        if self.is_valid_number(new_value) or new_value == "":
            self.entry_widget.delete(0, 'end')
            self.entry_widget.insert(0, new_value)
