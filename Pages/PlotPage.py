from Pages.BasePage import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from GlobalVariables import *


class PlotPageClass(BasePageClass):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Create plot frame within CustomTkinter with specific size
        self.plot_frame = ctk.CTkFrame(self, fg_color=infBlue, bg_color="white",
                                       width=650, height=350)
        self.plot_frame.grid(padx=20, pady=20, sticky="nsew")

        # Prevent frame from resizing
        self.plot_frame.grid_propagate(False)

        # Create Matplotlib figure with smaller size
        self.figure = plt.Figure(figsize=(6.2, 3.2), dpi=100)
        self.ax = self.figure.add_subplot(1, 1, 1)

        # Embed plot in CustomTkinter frame
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True)

        # Initialize data lists
        self.x_data = []
        self.y_data = []
        self.data_count = 0  # Counter for total data points
        self.max_points = 20

    def add_point(self, y_value):
        self.data_count += 1
        current_time = datetime.now().strftime('%H:%M:%S')

        if len(self.x_data) >= self.max_points:
            # Remove first element (oldest point)
            self.x_data.pop(0)
            self.y_data.pop(0)

        # Add new point at the end
        self.x_data.append(current_time)
        self.y_data.append(y_value)


    def update_plot(self):
        self.ax.clear()
        self.ax.plot(range(len(self.y_data)), self.y_data, marker='o', markersize=4)

        # Set x-axis ticks to show timestamps
        self.ax.set_xticks(range(len(self.x_data)))
        self.ax.set_xticklabels(self.x_data)

        # Adjust tick label sizes
        self.ax.tick_params(axis='both', labelsize=8)

        # Rotate and align the tick labels so they look better
        plt.setp(self.ax.get_xticklabels(), rotation=30, ha='right')

        # Set x-axis limits with small padding
        if self.x_data:
            self.ax.set_xlim(-0.5, len(self.x_data) - 0.5)

        # Set labels and title with smaller font sizes
        self.ax.set_xlabel('Time', fontsize=9)
        self.ax.set_ylabel('Pressure', fontsize=9)
        self.ax.set_title(f'Pressure Plot (Points {max(1, self.data_count - self.max_points + 1)}-{self.data_count})',
                          fontsize=10)

        # Adjust y-axis limits if we have data
        if self.y_data:
            y_min, y_max = min(self.y_data), max(self.y_data)
            y_range = y_max - y_min if y_max != y_min else 1.0
            # Add 10% padding to y-axis
            self.ax.set_ylim(
                y_min - 0.1 * y_range,
                y_max + 0.1 * y_range
            )

        # Adjust layout to better fit the smaller size
        self.figure.tight_layout(pad=1.2)
        self.canvas.draw()

    def clear_plot(self):
        self.x_data = []
        self.y_data = []
        self.data_count = 0
        self.ax.clear()
        self.canvas.draw()
