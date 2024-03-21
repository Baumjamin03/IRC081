# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:55:21 2024

@author: benj002
"""

import atexit
from SubFrame import *
# from IRC081 import IRC081
from decimal import *
from RS232 import *

# Define the custom window dimensions
WIDTH = 800
HEIGHT = 480


class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        """
        Initializes the IRUI081 for the IRC081 controller
        """
        super().__init__(*args, **kwargs)

        atexit.register(self.shutdown)

        self.configure(fg_color="black")

        # self.irc081 = IRC081()

        self.windowWidth = WIDTH
        self.windowHeight = HEIGHT

        self.title("IRUI082")
        self.geometry(f"{self.windowWidth}x{self.windowHeight}")

        self.state('normal')

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.frameDaq = DaqFrame(self)
        self.frameAnalogOut = AnalogFrame(self)
        self.frameEmission = EmissionFrame(self)
        self.framePressure = PressureFrame(self)
        self.frameVoltages = VoltagesFrame(self)

        self.upperRange = None
        self.lowerRange = None

        self.com = RS232Communication()
        self.com.open_port()
        self.RS232Listener = SerialListener(self.com, self.handle_serial_data)
        self.RS232Writer = SerialWriter(self.com)
        self.RS232Listener.start()

    def handle_serial_data(self, data):
        """
        Handles Data read from RS232.
        """
        print(f"Received data: {data}")

    def shutdown(self):
        """
        Executes on program termination. It resets the IRC081 Parameters and ends the RS232 communication.
        """
        self.irc081.measurement_end()
        self.RS232Listener.stop()
        self.com.close_port()

    def measurement_loop(self):
        """
        Calls itself and periodically updates measurement values.
        """
        if self.frameDaq.switch_var.get() == "on":
            self.update_values()
            self.after(1000, self.measurement_loop)

    def set_emission_curr(self):
        """
        Sets the Emission current for the IRG080.
        """
        current = self.frameEmission.entryCurrent.get()
        print("i emission set: " + current)
        self.irc081.set_emission(current)

    def switch_event(self):
        """
        Turns the IRG080 Measurements on/off.
        """
        if self.frameDaq.switch_var.get() == "on":
            self.set_emission_curr()
            self.irc081.measurement_start()
            self.measurement_loop()

        else:
            print("measurement end")
            self.irc081.measurement_end()

    def update_values(self):
        """
        Reads the Data from the IRC081 and Displays it.
        """
        self.irc081.refresh_controller_data()

        self.frameVoltages.uDeflector.value.set("{:.3f}".format(self.irc081.get_voltage_deflector()))
        self.frameVoltages.uWehnelt.value.set("{:.3f}".format(self.irc081.get_voltage_wehnelt()))
        self.frameVoltages.uFaraday.value.set("{:.3f}".format(self.irc081.get_voltage_faraday()))
        self.frameVoltages.uCage.value.set("{:.3f}".format(self.irc081.get_voltage_cage()))
        self.frameVoltages.uBias.value.set("{:.3f}".format(self.irc081.get_voltage_bias()))
        self.frameVoltages.iFil.value.set("{:.3f}".format(self.irc081.get_current_filament()))

        self.frameDaq.emissionDisplay.value.set("{:.5e}".format(self.irc081.get_emission_current()))

        self.framePressure.pressure.set("{:.5e}".format(self.irc081.get_pressure_mbar()))

        self.analog_out_handler()

    def analog_out_handler(self):
        """
        Calculates the output voltage in respect to the set range or auto range if enabled.
        Auto range will output twice the voltage it reads from the IColl (AI15) Analog Input.
        Defaults to auto range if no values are provided.
        """
        if self.frameAnalogOut.frameVoltageDisplay.check_var.get() or not (self.lowerRange and self.upperRange):
            voltage = self.irc081.get_ion_voltage() * 2
            self.frameAnalogOut.frameVoltageDisplay.value.set("{:.3f}".format(voltage))
        else:
            pressure = self.irc081.get_pressure_mbar()
            voltage = (pressure - self.lowerRange) / (self.upperRange - self.lowerRange) * 10
            self.frameAnalogOut.frameVoltageDisplay.value.set("{:.3f}".format(voltage))

    def set_range(self):
        """
        Sets the range provided by the range input entries.
        """
        try:
            upper_number = self.frameAnalogOut.entryUpperRange.entry.get()
            upper_exponent = self.frameAnalogOut.entryUpperRange.expEntry.get()
            upper_range = Decimal(f"{upper_number}e-{upper_exponent}")

            lower_number = self.frameAnalogOut.entryLowerRange.entry.get()
            lower_exponent = self.frameAnalogOut.entryLowerRange.expEntry.get()
            lower_range = Decimal(f"{lower_number}e-{lower_exponent}")

            print(f"Analog out range: {lower_range} - {upper_range}")
        except Exception as e:
            print("Error: " + str(e))
            return

        self.upperRange = upper_range
        self.lowerRange = lower_range


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
