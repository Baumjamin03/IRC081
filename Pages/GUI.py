from PIL import Image

from GlobalVariables import infBlue
import customtkinter as ctk

from Pages import *


class GraphicalInterface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.TitleBar = TrapezoidFrame(master=self, logo_path="Pictures/IFCN.SW_BIG.D.png")
        self.TitleBar.grid(row=0, column=1, sticky="nsew", pady=(0, 5))

        self.NavBar = TrapezoidFrame(master=self, invert=True)
        self.NavBar.grid(row=2, column=1, sticky="nsew", pady=(5, 0), padx=1)
        self.NavBar.grid_rowconfigure(0, weight=1)

        self.lblPage = ctk.CTkLabel(self.NavBar, text_color="white", text="", fg_color=infBlue,
                                    font=("Arial", 24, "bold"), bg_color=infBlue, justify="center")
        self.lblPage.pack(anchor="center", expand=True)

        # self.lblStatus = ctk.CTkLabel(self.NavBar, text="OFF", anchor="e", text_color="white", bg_color=infBlue,
        #                               font=("Arial", 18, "bold"), width=100, fg_color=infBlue)
        # self.lblStatus.grid(row=0, column=1, padx=70, sticky="nsew")

        self.content_frame = PageManagerClass(self, self.lblPage)
        self.content_frame.grid(row=1, column=0, sticky="nsew", columnspan=3, padx=5)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, minsize=55)  # Ensure TitleBar row height
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, minsize=55)  # Ensure NavBar row height

        self.corner_buttons = {
            "top_left": self.create_corner_button(0, 0, lambda: self.content_frame.show_page("Settings"),
                                                  "Pictures/settings.png"),
            "top_right": self.create_corner_button(0, 2, lambda: self.content_frame.show_page("Plot"),
                                                   "Pictures/operation.png"),
            "bottom_left": self.create_corner_button(2, 0, lambda: self.content_frame.show_page("Home"),
                                                     "Pictures/basic_user.png"),
            "bottom_right": self.create_corner_button(2, 2, lambda: self.content_frame.show_page("Info"),
                                                      "Pictures/help.png")
        }

    def create_corner_button(self,
                             row: int,
                             col: int,
                             command: callable = None,
                             logo_path: str = None) -> ctk.CTkButton:
        # Create image if logo path is provided
        if logo_path:
            # Open the image and get its original dimensions
            original_image = Image.open(logo_path)
            orig_width, orig_height = original_image.size

            # Calculate aspect ratio from original image
            aspect_ratio = orig_width / orig_height

            target_height = 30
            target_width = int(target_height * aspect_ratio)

            button_image = ctk.CTkImage(
                light_image=original_image,
                dark_image=original_image,
                size=(target_width, target_height)
            )
        else:
            button_image = None

        button = ctk.CTkButton(
            self,
            text="",
            image=button_image,
            compound="left",
            text_color="#5D74A1",
            command=command,
            fg_color="white",
            hover_color=infBlue,
            hover=False
        )
        button.grid(row=row, column=col, sticky="nsew")
        return button
