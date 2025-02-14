import tkinter as tk
import customtkinter as ctk
from PIL import Image
from GlobalVariables import infBlue


class BasePageClass(ctk.CTkFrame):
    def __init__(self,
                 master: any,
                 **kwargs: any):
        super().__init__(master, fg_color=infBlue, bg_color="white", corner_radius=10, **kwargs)


class TouchEntry(ctk.CTkEntry):
    def __init__(self, master, row, col, pady=10, **kwargs):
        super().__init__(master, height=50, justify="center", **kwargs)
        self.grid(row=row, column=col, pady=pady)


class ValueDisplay(ctk.CTkFrame):
    def __init__(self, master, text, row=0, col=0, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=5, border_color="white", border_width=5, **kwargs)
        self.grid(row=row, column=col, sticky="nsew", pady=5, padx=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.lblName = ctk.CTkLabel(self, text=text, anchor="center", height=15, width=100, corner_radius=5, padx=3,
                                    font=("Arial", 15, "bold"), text_color="black")
        self.lblName.grid(row=0, column=0, sticky="ew", padx=3)
        self.value = ctk.DoubleVar(value=12.34)
        self.lblValue = ctk.CTkLabel(self, textvariable=self.value, anchor="center", height=20, width=100,
                                     text_color="black", corner_radius=5, font=("Arial", 14,))
        self.lblValue.grid(row=1, column=0, sticky="ew", padx=3)


class HorizontalValueDisplay(ValueDisplay):
    def __init__(self, *args, value="", **kwargs):
        super().__init__(*args, **kwargs)
        self.grid(pady=10, padx=10, sticky="ns")
        self.lblValue.grid(row=0, column=1, padx=5)
        self.lblName.configure(anchor="e")
        self.lblValue.configure(anchor="w")
        self.s_value = ctk.StringVar(value=value)
        self.lblValue.configure(textvariable=self.s_value)


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

    def draw_trapezoid(self) -> None:
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

    def load_logo(self) -> None:
        """Load and display the logo image inside the trapezoid"""
        # Use PIL to open the image (supports formats like PNG, JPEG, etc.)

        self.logo_image = ctk.CTkImage(light_image=Image.open(self.logo_path), size=(174, 35))

        self.lblI = ctk.CTkLabel(self, image=self.logo_image, text="", bg_color=infBlue)
        self.lblI.pack(expand=True)

    def on_resize(self, event) -> None:
        """Handle resize events"""
        self.width = event.width
        self.height = event.height
        self.draw_trapezoid()
