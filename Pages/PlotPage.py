from Pages.BasePage import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.dates as mdates
from GlobalVariables import *


class PlotPageClass(BasePageClass):
    def __init__(self,
                 master: any,
                 **kwargs: any):
        """
        creates a page based on a ctk.CTkFrame that contains a data plotter
        :param master: ctk.CTkFrame containing the plotpage
        :param kwargs: passed onto ctk.CTkFrame
        """
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.plot_frame = ctk.CTkFrame(self, fg_color=infBlue, bg_color="white",
                                       width=650, height=350)
        self.plot_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.plot_frame.grid_propagate(False)

        self.figure = plt.Figure(figsize=(6.2, 3.0), dpi=100)
        self.ax = self.figure.add_subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True)

        self.x_data = []
        self.y_data = []
        self.data_count = 0  # Counter for total data points
        self.max_points = 20

        self.update_plot()

    def add_point(self, y_value) -> None:
        """
        appends a data point with timestamp
        :param y_value: pressure value
        """
        current_time = datetime.now()

        if len(self.x_data) >= self.max_points:
            self.x_data.pop(0)
            self.y_data.pop(0)

        self.x_data.append(current_time)
        self.y_data.append(y_value)

    def update_plot(self) -> None:
        """
        updates the graphical elements of the plot
        """
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, marker='o', markersize=4)

        # Format the x-axis to display timestamps
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        self.ax.set_ylabel('Pressure in mBar', fontsize=14)
        self.ax.set_title('Pressure Plot', fontsize=14)

        # Rotate x-axis labels for better readability
        self.figure.autofmt_xdate()

        self.canvas.draw()

    def clear_plot(self) -> None:
        """
        clears the plot
        """
        self.x_data = []
        self.y_data = []
        self.ax.clear()
        self.canvas.draw()
