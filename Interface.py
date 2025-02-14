from threading import Thread
from PIL import Image
import asyncio
import time
import atexit
import platform
import customtkinter as ctk

from Pages import *

if platform.system() != "Windows":
    from Hardware_Control import *

infBlue = "#24517F"
txtColor = "white"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color="white")

        self.geometry("600x280")
        if platform.system() == "Windows":
            self.geometry("800x480")

        self.com = None
        port_toggle = False
        while self.com is None and platform.system() != "Windows":
            try:
                if port_toggle:
                    port_toggle = False
                    self.com = RS232Communication()
                else:
                    port_toggle = True
                    self.com = RS232Communication(port='/dev/ttyS0')
                if self.com.is_open:
                    self.com.close_port()
                self.com.open_port()
            except Exception as er:
                print(er)
                self.com = None
                time.sleep(1)

        if self.com is not None:
            self.RS232Listener = SerialListener(self.com, self.handle_serial_data)
            self.RS232Listener.start()

        self.uOut = 0
        self.lowerRange = 0
        self.upperRange = 0
        self.dPot = None

        if platform.system() != "Windows":
            try:
                self.dPot = MCP4725()
            except Exception as er:
                print(er)

        self.irc081 = None
        while self.irc081 is None:

            if platform.system() == "Windows":
                break  # important break for simulating GUI on a desktop

            try:
                self.irc081 = IRC081()
                atexit.register(self.shutdown)
            except OSError as er:
                print("no IRC081 found, Error: " + str(er))
                start_screen = ctk.CTk()
                start_screen.geometry("400x200")
                lbl_start = ctk.CTkLabel(start_screen, text="Please connect IRC081")
                lbl_start.pack(pady=50)
                start_screen.after(5000, start_screen.destroy)
                start_screen.mainloop()
                time.sleep(5)
                # continue
            break

        self.running = False

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

        self.content_frame.add_page("Home", HomePageClass(self.content_frame, sw_event=self.switch_event,
                                                          emission_setter=self.set_emission_curr))
        self.content_frame.add_page("Settings", SettingsPageClass(self.content_frame, range_setter=self.set_range))
        self.content_frame.add_page("Plot", PlotPageClass(self.content_frame))
        self.content_frame.add_page("Info", InfoPageClass(self.content_frame))

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
        # Show the default page (Home)
        self.content_frame.show_page("Home")

        if self.irc081 is not None:
            print("starting meas. thread")
            self.start_loop_in_thread(self.irc081.refresh_controller_data)

    def shutdown(self) -> None:
        """
        Executes on program termination. It resets the IRC081 Parameters and ends the RS232 communication
        """
        if self.irc081 is not None:
            self.irc081.measurement_end()
            self.RS232Listener.stop()
            self.com.close_port()

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
        )
        button.grid(row=row, column=col, sticky="nsew")
        return button

    def switch_event(self) -> None:
        """
        Turns the IRG080 Measurements on/off.
        """
        if not self.running:
            self.running = True
            self.content_frame.pages["Home"].emOn.configure(fg_color="#3F7432")
            self.set_emission_curr()
            self.measurement_loop()
            if self.irc081 is not None:
                self.irc081.measurement_start()
        else:
            self.running = False
            self.content_frame.pages["Home"].emOn.configure(fg_color="#BBD396")
            print("measurement end")
            if self.irc081 is not None:
                self.irc081.measurement_end()

    def set_emission_curr(self) -> None | str:
        """
        Sets the Emission current for the IRG080.
        """
        current = self.content_frame.pages["Home"].entryEmission.get()
        print("i emission set: " + current)
        if self.irc081 is not None:
            try:
                self.irc081.set_emission(Decimal(current))
            except DecimalException as er:
                print(str(er))
                return "invalid value"
            return None

    def measurement_loop(self) -> None:
        """
        Calls itself and periodically updates measurement values.
        """
        if self.running:
            self.after(1000, self.measurement_loop)
            if self.irc081 is not None:
                self.update_values()
                self.update_aout()
                self.analogue_out_handler()

    def update_values(self) -> None:
        """
        Reads the Data from the IRC081 and Displays it.
        """
        self.content_frame.pages["Plot"].add_point(self.irc081.get_pressure_mbar())

        if self.content_frame.current_page == "Home":
            self.content_frame.pages["Home"].Voltages["Wehnelt"].value.set(
                "{:.3f}".format(self.irc081.get_voltage_wehnelt()))
            self.content_frame.pages["Home"].Voltages["Cage"].value.set(
                "{:.3f}".format(self.irc081.get_voltage_cage()))
            self.content_frame.pages["Home"].Voltages["Faraday"].value.set(
                "{:.3f}".format(self.irc081.get_voltage_faraday()))
            self.content_frame.pages["Home"].Voltages["Bias"].value.set(
                "{:.3f}".format(self.irc081.get_voltage_bias()))
            self.content_frame.pages["Home"].Voltages["Deflector"].value.set(
                "{:.3f}".format(self.irc081.get_voltage_deflector()))
            self.content_frame.pages["Home"].Voltages["Filament"].value.set(
                "{:.3f}".format(self.irc081.get_current_filament()))

            self.content_frame.pages["Home"].pressure.set("{:.5e}".format(self.irc081.get_pressure_mbar()))
            self.content_frame.pages["Home"].transmission.set("{:.2f}".format(self.irc081.get_transmission()))

        elif self.content_frame.current_page == "Settings":
            self.content_frame.pages["Settings"].values["iEmission"].value.set(
                "{:.3f}".format(self.irc081.get_emission_current()))
            self.content_frame.pages["Settings"].values["iCage"].value.set(
                "{:.3f}".format(self.irc081.get_cage_current()))
            self.content_frame.pages["Settings"].values["iFaraday"].value.set(
                "{:.3f}".format(self.irc081.get_faraday_current()))
            self.content_frame.pages["Settings"].values["iCollector"].value.set(
                "{:.3f}".format(self.irc081.get_ion_current()))
            self.content_frame.pages["Settings"].lblOut.value.set(
                "{:.3f}".format(self.uOut))

        elif self.content_frame.current_page == "Plot":
            self.content_frame.pages["Plot"].update_plot()

    def update_aout(self) -> None:
        """
        Calculates the output voltage in respect to the set range or auto range if enabled.
        Auto range will output twice the voltage it reads from the IColl (AI15) Analog Input.
        Defaults to auto range if no values are provided
        """
        try:
            voltage = Decimal(self.uOut)
            d_value = voltage * 4096 // 10 - 1
            self.dPot.set_analogue_out(int(d_value))
        except Exception as er:
            print(er)

    def analogue_out_handler(self) -> None:
        pressure = Decimal(self.irc081.get_pressure_mbar())

        try:
            self.uOut = (pressure - self.lowerRange) / (self.upperRange - self.lowerRange) * 10
            print(f"Pressure: {pressure}, Range: {self.lowerRange}-{self.upperRange}, Output: {self.uOut}")
            self.content_frame.pages["Settings"].lblOut.value.set("{:.3f}".format(self.uOut))
        except DecimalException as er:
            print("Analogue Handler ERR: " + str(er))

    def set_range(self) -> None:
        try:
            lower_range = Decimal(self.content_frame.pages["Settings"].entryLower.get())
            upper_range = Decimal(self.content_frame.pages["Settings"].entryUpper.get())
            print(f"new ranges: {upper_range} to {lower_range}")
        except Exception as er:
            print("Range Error: " + str(er))
            return

        self.lowerRange = lower_range
        self.upperRange = upper_range
        print(f"new real ranges: {self.upperRange} to {self.lowerRange}")

    def start_loop_in_thread(self, func) -> None:
        """
        Takes a function, creates an async Loop and runs it in a Thread
        :param func: any function to be run in a separate Thread
        """
        def run_loop(_loop):
            asyncio.set_event_loop(_loop)
            loop.run_forever()

        loop = asyncio.new_event_loop()
        loop_thread = Thread(target=run_loop, args=(loop,), daemon=True)
        loop_thread.start()
        asyncio.run_coroutine_threadsafe(func(), loop)

    def handle_serial_data(self,
                           data) -> None | str:
        """
        serial data handling for more information visit:
        https://colla.inficon.com/display/VCRD/RS232+Protocoll
        """
        while data.endswith(b'\r') or data.endswith(b'\n'):
            data = data[:len(data) - 1]
        response = data + b'\r\n'

        if len(data) < 2:
            return response + b'Error, cmd too short\r\n'

        command_code = data[:2]
        print("command: " + str(command_code))

        writing = False
        value = None
        if len(data) > 2:
            writing = data[2:3] == b';'
            if not writing:
                return response + b'cmd too long or invalid writing operator\r\n'
            value = data[3:].decode()

        if command_code == b'AL':  # Analogue range lower
            if writing:
                if 'E-' in value:
                    try:
                        self.content_frame.pages["Setting"].entryLower.set(value)
                        self.set_range()
                    except ValueError:
                        response += b'value Error'
                else:
                    response += b'missing [E-]'
            else:
                response += str(self.lowerRange).encode()
        elif command_code == b'AU':  # Analogue range upper
            if writing:
                if 'E-' in value:
                    try:
                        self.content_frame.pages["Setting"].entryUpper.set(value)
                        self.set_range()
                    except ValueError:
                        response += b'value Error'
                else:
                    response += b'missing [E-]'
            else:
                response += str(self.upperRange).encode()
        elif command_code == b'AV':  # Analogue Voltage
            response += str(self.uOut).encode()
        elif command_code == b'EC':  # Emission current
            if writing:
                self.content_frame.pages["Home"].entryEmission.delete(0, ctk.END)
                self.content_frame.pages["Home"].entryEmission.insert(0, value)
                answ = self.set_emission_curr()
                if answ is not None:
                    response += answ
            else:
                response += str(self.content_frame.pages["Home"].entryEmission.get()).encode()
        elif command_code == b'ME':  # Measurement on/off
            if writing:
                if value == "1":
                    if not self.running:
                        self.switch_event()
                else:
                    if self.running:
                        self.switch_event()
            else:
                response += self.running
        elif command_code == b'VW':  # Get Voltage Wehnelt
            response += str(self.content_frame.pages["Home"].Voltages["Wehnelt"].value.get()).encode()
        elif command_code == b'VC':  # Get Voltage Cage
            response += str(self.content_frame.pages["Home"].Voltages["Cage"].value.get()).encode()
        elif command_code == b'VF':  # Get Voltage Faraday
            response += str(self.content_frame.pages["Home"].Voltages["Faraday"].value.get()).encode()
        elif command_code == b'VB':  # Get Voltage Bias
            response += str(self.content_frame.pages["Home"].Voltages["Bias"].value.get()).encode()
        elif command_code == b'VD':  # Get Voltage Deflector
            response += str(self.content_frame.pages["Home"].Voltages["Deflector"].value.get()).encode()
        elif command_code == b'IF':  # Get Filament Current
            response += str(self.content_frame.pages["Home"].Voltages["Current"].value.get()).encode()
        elif command_code == b'PR':  # Get Pressure
            response += str(self.content_frame.pages["Home"].pressure.get()).encode()
        else:
            response += b'unknown command'

        if response.endswith(b'\r\n'):
            return response
        else:
            return response + b'\r\n'


if __name__ == "__main__":
    root = App()
    if platform.system() != "Windows":
        root.after(500, lambda: root.wm_attributes('-fullscreen', 'true'))
    root.mainloop()
