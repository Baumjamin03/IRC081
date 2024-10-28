import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

infBlue = "#24517F"
txtColor = "white"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color="white")

        self.geometry("800x480")
        self.title("Control Interface")

        self.TitleBar = TrapezoidFrame(master=self, logo_path="./IFCN.SW_BIG.D.png")
        self.TitleBar.grid(row=0, column=1, sticky="nsew", pady=(0, 5))

        self.NavBar = TrapezoidFrame(master=self, height=30, invert=True)
        self.NavBar.grid(row=2, column=1, sticky="nsew", pady=(5, 0))
        self.NavBar.grid_rowconfigure(0, weight=1)
        self.NavBar.grid_columnconfigure((0, 1), weight=1)

        self.lblPage = ctk.CTkLabel(self.NavBar, text_color="white", text="", fg_color=infBlue, width=100, anchor="w",
                                    font=("Arial", 18, "bold"))
        self.lblPage.grid(row=0, column=0, padx=70, sticky="nsew")

        self.lblStatus = ctk.CTkLabel(self.NavBar, text="OFF", anchor="e", font=("Arial", 18, "bold"), width=100,
                                      fg_color=infBlue)
        self.lblStatus.grid(row=0, column=1, padx=70, sticky="nsew")

        self.content_frame = PageManager(self, self.lblPage)
        self.content_frame.grid(row=1, column=0, sticky="nsew", columnspan=3, padx=5)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.content_frame.add_page("Home", HomePage(self.content_frame))
        self.content_frame.add_page("Settings", SettingsPage(self.content_frame))
        self.content_frame.add_page("Plot", PlotPage(self.content_frame))
        self.content_frame.add_page("Info", InfoPage(self.content_frame))

        self.corner_buttons = {
            "top_left": self.create_corner_button("⚙️", 0, 0, lambda: self.content_frame.show_page("Settings")),
            "top_right": self.create_corner_button("👁️", 0, 2, lambda: self.content_frame.show_page("Plot")),
            "bottom_left": self.create_corner_button("👤", 2, 0, lambda: self.content_frame.show_page("Home")),
            "bottom_right": self.create_corner_button("🔍", 2, 2, lambda: self.content_frame.show_page("Info"))
        }
        # Show the default page (Home)
        self.content_frame.show_page("Home")

    def create_corner_button(self, text: str, row: int, col: int, command) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self,
            text=text,
            width=60,
            height=60,
            text_color="#5D74A1",
            command=command,
            fg_color="white",
            hover_color=infBlue,
            font=("Arial", 24, "bold")
        )
        button.grid(row=row, column=col, sticky="nsew")
        return button


class BasePage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=infBlue, bg_color="white", corner_radius=10, **kwargs)


class PageManager(BasePage):
    def __init__(self, master, lbl_page, **kwargs):
        super().__init__(master, **kwargs)
        self.current_page = None
        self.pages = {}
        self.lbl_page = lbl_page
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.add_page("Numpad", NumpadPage(self))

    def add_page(self, page_name, page):
        """Add a page to the manager"""
        self.pages[page_name] = page
        page.grid(row=0, column=0, sticky="nsew")
        if not self.current_page:
            self.current_page = page_name

    def show_page(self, page_name):
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

    def show_numpad(self, entry, caller_page):
        self.pages["Numpad"].show(entry, caller_page)


class NumericKeypad(ctk.CTkFrame):
    def __init__(self, master, entry_widget=None, **kwargs):
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

    def is_valid_number(self, value):
        """Check if the resulting string would be a valid positive number (including zero)"""
        try:

            # Don't allow negative signs at all
            if '-' in value:
                for s in value.split('E'):
                    if s.count('E') > 1:
                        return False

            # Check for valid scientific notation
            if 'E' in value:
                if value.count('E') > 1:
                    return False

                return True

            # For regular numbers
            if value.count('.') > 1:
                return False

            # Convert to float and check if positive
            # num = float(value)
            # return num >= 0
            return True
        except ValueError:
            return False

    def button_click(self, value):
        if not self.entry_widget:
            return

        current = self.entry_widget.get()

        if value == '⌫':
            new_value = current[:-1]
        elif value == '↓':
            self.master.confirm()
            return
        else:
            if value == '-' and current:
                return
            if value == 'E':
                if 'E' in current or not current:
                    return
            if value == '.' and '.' in current.split('E')[0]:
                return

            new_value = current + value

        if self.is_valid_number(new_value) or new_value == "":
            self.entry_widget.delete(0, 'end')
            self.entry_widget.insert(0, new_value)


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

    def show(self, entry_widget, og_page_name):
        """Prepare and show the numpad page"""
        self.target_entry = entry_widget
        self.og_page = og_page_name
        self.original_value = entry_widget.get()
        self.display.delete(0, 'end')
        self.display.insert(0, self.original_value)
        self.page_manager.show_page("Numpad")
        self.display.focus()

    def confirm(self):
        """Confirm the entered value and return to previous page"""
        if self.target_entry:
            self.target_entry.delete(0, 'end')
            self.target_entry.insert(0, self.display.get())
        self.cleanup()

    def cancel(self):
        """Cancel the entry and return to previous page"""
        if self.target_entry and self.original_value is not None:
            self.target_entry.delete(0, 'end')
            self.target_entry.insert(0, self.original_value)
        self.cleanup()

    def cleanup(self):
        """Reset the numpad state"""
        self.target_entry = None
        self.original_value = None
        self.display.delete(0, 'end')
        self.page_manager.show_page(self.og_page)
        self.og_page = None

    def on_page_leave(self):
        """Called when switching away from numpad page"""
        if self.target_entry:
            self.cancel()


class HomePage(BasePage):
    def __init__(self, master):
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
                                border_color="white", fg_color="green")
        self.emOn.grid(row=0, column=0)

        self.entryEmission = TouchEntry(self.emFrame, 1, 0)
        self.entryEmission.bind("<Button-1>", lambda e: master.show_numpad(self.entryEmission, "Home"))

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
    def __init__(self, master, row, col, **kwargs):
        super().__init__(master, height=40, **kwargs)
        self.grid(row=row, column=col)


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
    def __init__(self, master):
        super().__init__(master)


class TrapezoidFrame(ctk.CTkFrame):
    def __init__(
            self,
            master: any,
            height: int = 30,
            invert: bool = 0,
            logo_path: str = None,
            **kwargs
    ):
        # Initialize with 0 border width to avoid the standard frame border
        super().__init__(master, height=height, fg_color="white", **kwargs)

        # Create canvas for the trapezoid shape
        self.canvas = tk.Canvas(
            self,
            height=height,
            highlightthickness=0,
            bg="white"  # Use master's background color
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Create the trapezoid shape
        self.fg_color = infBlue  # Use provided color or default blue
        self.width = 300
        self.height = height
        self.invert = invert

        # Draw initial shape
        self.draw_trapezoid()
        self.logo_path = logo_path

        self.lblI = None
        self.logo_image = None
        if logo_path:
            self.load_logo()

        # Bind resize event
        self.bind("<Configure>", self.on_resize)

    def draw_trapezoid(self):
        """Draw the trapezoid shape on the canvas"""
        self.canvas.delete("trapezoid")  # Clear previous shape

        radius = 5

        # Create trapezoid points
        if self.invert:
            points = [
                self.height, 0,  # Top left
                self.width - self.height, 0,  # Top right
                self.width, self.height,  # Bottom right
                0, self.height  # Bottom left
            ]
        else:
            points = [
                0, 0,  # Top left
                self.width, 0,  # Top right
                self.width - self.height, self.height,  # Bottom right
                self.height, self.height  # Bottom left
            ]

        # Create shape
        self.canvas.create_polygon(
            points,
            fill=self.fg_color,
            outline=self.fg_color,
            tags="trapezoid",
            joinstyle="miter"
        )

    def load_logo(self):
        """Load and display the logo image inside the trapezoid"""
        # Use PIL to open the image (supports formats like PNG, JPEG, etc.)

        self.logo_image = ctk.CTkImage(light_image=Image.open(self.logo_path), size=(174, 35))

        self.lblI = ctk.CTkLabel(self, image=self.logo_image, text="", bg_color=infBlue)
        self.lblI.pack(expand=True)

    def on_resize(self, event):
        """Handle resize events"""
        self.width = event.width
        self.height = event.height
        self.draw_trapezoid()


if __name__ == "__main__":
    root = App()
    # root.after(500, lambda: root.wm_attributes('-fullscreen', 'true'))
    root.mainloop()
