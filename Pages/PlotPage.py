from Pages.BasePage import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from GlobalVariables import *


class PlotPageClass(BasePageClass):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Create plot frame within CustomTkinter
        self.plot_frame = ctk.CTkFrame(self, fg_color=infBlue, bg_color="white")
        self.plot_frame.grid(padx=50, pady=50, sticky="nsew")

        # Create Matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(8, 5))

        # Embed plot in CustomTkinter frame
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True)

        # Initialize data lists
        self.x_data = []
        self.y_data = []

    def add_point(self, y_value):
        current_time = datetime.now()
        self.x_data.append(current_time)
        self.y_data.append(y_value)

    def update_plot(self):
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, marker='o')

        self.ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
        plt.setp(self.ax.get_xticklabels(), rotation=45)

        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Real-time Plot')

        self.figure.tight_layout()
        self.canvas.draw()

    def clear_plot(self):
        self.x_data = []
        self.y_data = []
        self.ax.clear()
        self.canvas.draw()
