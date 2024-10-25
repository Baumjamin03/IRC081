import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

infBlue = "#24517F"
txtColor = "white"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.pages = {}
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

        self.content_frame = ctk.CTkFrame(self, fg_color=infBlue, corner_radius=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew", columnspan=3, padx=5)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.pages["Home"] = HomePage(self.content_frame)
        self.pages["Settings"] = SettingsPage(self.content_frame)
        self.pages["Plot"] = PlotPage(self.content_frame)
        self.pages["Info"] = InfoPage(self.content_frame)

        # Place all pages in the same location in the content frame
        for page in self.pages.values():
            page.place(relwidth=1, relheight=1)

        self.corner_buttons = {
            "top_left": self.create_corner_button("⚙️", 0, 0, lambda: self.show_page("Settings")),
            "top_right": self.create_corner_button("👁️", 0, 2, lambda: self.show_page("Plot")),
            "bottom_left": self.create_corner_button("👤", 2, 0, lambda: self.show_page("Home")),
            "bottom_right": self.create_corner_button("🔍", 2, 2, lambda: self.show_page("Info"))
        }
        # Show the default page (Home)
        self.show_page("Home")

    def show_page(self, page_name: str):
        """Show the selected page by lifting it to the front"""
        page = self.pages.get(page_name)
        if page:
            self.lblPage.configure(text=page_name)
            page.lift()

    def create_corner_button(self, text: str, row: int, col: int, command) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self,
            text=text,
            width=60,
            height=60,
            text_color="#5D74A1",
            command=command,
            fg_color="white",
            hover_color=infBlue
        )
        button.grid(row=row, column=col, sticky="nsew")
        return button


class BasePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=infBlue, bg_color="white", corner_radius=10)


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
