import customtkinter as ctk
from GlobalVariables import *
from decimal import *


class BasePage(ctk.CTkFrame):
    def __init__(self,
                 master: any,
                 **kwargs: any):
        super().__init__(master, fg_color=infBlue, bg_color="white", corner_radius=10, **kwargs)


class PageManager(BasePage):
    def __init__(self,
                 master: any,
                 lbl_page: ctk.CTkLabel,
                 **kwargs: any):
        super().__init__(master, **kwargs)
        self.current_page = None
        self.pages = {}
        self.lbl_page = lbl_page
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.add_page("Numpad", NumpadPage(self))

    def add_page(self,
                 page_name: str,
                 page) -> None:
        """Add a page to the manager"""
        self.pages[page_name] = page
        page.grid(row=0, column=0, sticky="nsew")
        if not self.current_page:
            self.current_page = page_name

    def show_page(self,
                  page_name: str) -> None:
        """Switch to a specific page"""
        if page_name in self.pages:
            # Notify current page it's being hidden
            if self.current_page and hasattr(self.pages[self.current_page], "on_page_leave"):
                self.pages[self.current_page].on_page_leave()

            # Show new page
            self.pages[page_name].lift()
            self.current_page = page_name

            # Notify new page it's being shown
            if hasattr(self.pages[page_name], "on_page_enter"):
                self.pages[page_name].on_page_enter()

            self.lbl_page.configure(text=page_name)

    def show_numpad(self,
                    entry: ctk.CTkEntry,
                    caller_page) -> None:
        self.pages["Numpad"].show(entry, caller_page)


class NumpadPage(BasePage):
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
                 master: NumpadPage,
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


class HomePage(BasePage):
    def __init__(self,
                 master: any,
                 sw_event: callable,
                 emission_setter: callable):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.vFrame = ctk.CTkFrame(self, fg_color=infBlue)
        self.vFrame.grid(row=1, column=0, sticky="ew", padx=10, pady=5, columnspan=2)

        self.vFrame.grid_rowconfigure(0, weight=1)
        self.vFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.Voltages = {
            "Bias": ValueDisplay(self.vFrame, "Bias (V):", 0, 0),
            "Wehnelt": ValueDisplay(self.vFrame, "Wehnelt (V):", 0, 1),
            "Faraday": ValueDisplay(self.vFrame, "Faraday (V):", 0, 2),
            "Cage": ValueDisplay(self.vFrame, "Cage (V):", 0, 3),
            "Deflector": ValueDisplay(self.vFrame, "Deflector (V):", 0, 4),
            "Filament": ValueDisplay(self.vFrame, "Filament (A):", 0, 5)
        }

        self.emFrame = ctk.CTkFrame(self, fg_color=infBlue)
        self.emFrame.grid(row=0, column=0)

        self.emOn = StartButton(self.emFrame, text="", corner_radius=30, height=60, width=60, border_width=5,
                                border_color="white", fg_color="#BBD396", command=sw_event, hover=False)
        self.emOn.grid(row=0, column=0)

        self.lblEmission = ctk.CTkLabel(self.emFrame, text="Emission in uA:", font=("Arial", 18, "bold"))
        self.lblEmission.grid(row=1, column=0, pady=(10, 0))

        self.entryEmission = TouchEntry(self.emFrame, 2, 0, font=("Arial", 18, "normal"))
        self.entryEmission.insert(0, "30")
        self.entryEmission.bind("<Button-1>", lambda event: master.show_numpad(self.entryEmission, "Home"))
        self.entryEmission.grid(sticky="ew")

        self.btnEmission = ctk.CTkButton(self.emFrame, bg_color=infBlue, text_color="white", text="Set Emission",
                                         height=40, command=emission_setter)
        self.btnEmission.grid(row=3, column=0, pady=5)

        self.pressFrame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.pressFrame.grid(row=0, column=1, sticky="nsew", pady=30, padx=30)
        self.pressFrame.grid_columnconfigure(0, weight=1)
        self.pressFrame.grid_rowconfigure(0, weight=1)

        self.pressure = ctk.DoubleVar(value=1.0083e-5)
        self.lblPressure = ctk.CTkLabel(self.pressFrame, textvariable=self.pressure, font=("Arial", 64, "bold"),
                                        anchor="center", text_color="black")
        self.lblPressure.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)

        self.transmissionFrame = ctk.CTkFrame(self.pressFrame, fg_color="white")
        self.transmissionFrame.grid(row=1, column=0, sticky="nsew", pady=10, padx=(50, 5))
        self.transmission = ctk.DoubleVar(value=98.55)
        ctk.CTkLabel(self.transmissionFrame, font=("Arial", 36, "bold"), text_color="black",
                     text="Transmission: ", fg_color="white", anchor="e").grid(row=0, column=0, padx=2)

        self.lblTransmission = ctk.CTkLabel(self.transmissionFrame, textvariable=self.transmission,
                                            font=("Arial", 36, "bold"),
                                            anchor="center", text_color="black")
        self.lblTransmission.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(self.transmissionFrame, font=("Arial", 36, "bold"), text_color="black",
                     text="%", anchor="w", fg_color="white").grid(row=0, column=2, sticky="nsew")


class StartButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class TouchEntry(ctk.CTkEntry):
    def __init__(self, master, row, col, pady=5, **kwargs):
        super().__init__(master, height=50, justify="center", **kwargs)
        self.grid(row=row, column=col, pady=pady)


class ValueDisplay(ctk.CTkFrame):
    def __init__(self, master, text, row, col, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=5, border_color="white", border_width=5, **kwargs)
        self.grid(row=row, column=col, sticky="nsew", pady=5, padx=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.lblName = ctk.CTkLabel(self, text=text, anchor="center", height=15, width=100, corner_radius=5, padx=3,
                                    font=("Arial", 14, "bold"), text_color="black")
        self.lblName.grid(row=0, column=0, sticky="ew", padx=3)
        self.value = ctk.DoubleVar(value=12.34)
        self.lblValue = ctk.CTkLabel(self, textvariable=self.value, anchor="center", height=20, width=100,
                                     text_color="black", corner_radius=5)
        self.lblValue.grid(row=1, column=0, sticky="ew", padx=3)


class PlotPage(BasePage):
    def __init__(self, master):
        super().__init__(master)


class InfoPage(BasePage):
    def __init__(self, master):
        super().__init__(master)


class SettingsPage(BasePage):
    def __init__(self, master: any):
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frameRange = ctk.CTkFrame(self, fg_color=infBlue, bg_color=infBlue)
        self.frameRange.grid(row=0, column=0)

        self.frameAnalogue = ctk.CTkFrame(self, fg_color=infBlue, bg_color=infBlue)
        self.frameAnalogue.grid(row=0, column=1)

        self.entryUpper = TouchEntry(self.frameRange, 0, 0)
        self.entryUpper.insert(0, "5E-6")
        self.entryUpper.bind("<Button-1>", lambda event: master.show_numpad(self.entryUpper, "Settings"))

        self.entryLower = TouchEntry(self.frameRange, 1, 0)
        self.entryLower.insert(0, "5E-9")
        self.entryLower.bind("<Button-1>", lambda event: master.show_numpad(self.entryLower, "Settings"))

        self.lblOut = ValueDisplay(self.frameAnalogue, "Analogue Out (V):", 0, 0)

        self.frameValues = ctk.CTkFrame(self, fg_color=infBlue, bg_color=infBlue)
        self.frameValues.grid(row=1, column=0, columnspan=2, pady=3)
        self.values = {
            "iFaraday": ValueDisplay(self.frameValues, "Faraday (A):", 0, 0),
            "iCage": ValueDisplay(self.frameValues, "Cage (A):", 0, 1),
            "iEmission": ValueDisplay(self.frameValues, "Emission (A):", 0, 2),
            "iCollector": ValueDisplay(self.frameValues, "Collector (A):", 0, 3)
        }
