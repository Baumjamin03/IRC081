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

        # Create main layout
        self.create_layout()

    def create_layout(self) -> None:
        # Create corner buttons frame
        self.corner_buttons = {
            "top_left": self.create_corner_button("⚙️", 0, 0, lambda: self.show_page("Settings")),
            "top_right": self.create_corner_button("👁️", 0, 2, lambda: self.show_page("Monitor")),
            "bottom_left": self.create_corner_button("👤", 2, 0, lambda: self.show_page("Home")),
            "bottom_right": self.create_corner_button("🔍", 2, 2, lambda: self.show_page("Details"))
        }

        self.TitleBar = TrapezoidFrame(master=self, height=30, logo_path="./IFCN.SW_BIG.D.png")
        self.TitleBar.grid(row=0, column=1, sticky="nsew", pady=(0, 5))

        self.NavBar = TrapezoidFrame(master=self, height=30, invert=True)
        self.NavBar.grid(row=2, column=1, sticky="nsew", pady=(5, 0))

        self.content_frame = ctk.CTkFrame(self, fg_color=infBlue, corner_radius=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew", columnspan=3, padx=5)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_corner_button(self, text: str, row: int, col: int, command) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self,
            text=text,
            width=50,
            height=50,
            command=command,
            fg_color="#2B87D3",
            hover_color="#1B77C3"
        )
        button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        return button


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

        self.logo_image = ctk.CTkImage(light_image=Image.open(self.logo_path), size=(200, 40))

        self.lblI = ctk.CTkLabel(self, image=self.logo_image, text="", bg_color=infBlue)
        self.lblI.pack(expand=True)

    def on_resize(self, event):
        """Handle resize events"""
        self.width = event.width
        self.height = event.height
        self.draw_trapezoid()


    def set_color(self, color: str):
        """Update the trapezoid color"""
        self.fg_color = color
        self.draw_trapezoid()


if __name__ == "__main__":
    root = App()
    # root.after(500, lambda: root.wm_attributes('-fullscreen', 'true'))
    root.mainloop()
