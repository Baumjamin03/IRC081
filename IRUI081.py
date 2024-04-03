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


class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        """
        Initializes the IRUI081 for the IRC081 controller
        """
        super().__init__(*args, **kwargs)

        # atexit.register(self.shutdown)

        self.configure(fg_color="black")

        # self.irc081 = IRC081()

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.frameDaq = DaqFrame(self)
        self.frameAnalogOut = AnalogFrame(self)
        self.frameEmission = EmissionFrame(self)
        self.framePressure = PressureFrame(self)
        self.frameVoltages = VoltagesFrame(self)

        self.upperRange = None
        self.lowerRange = None

        # self.com = RS232Communication()
        # self.com.open_port()
        # self.RS232Listener = SerialListener(self.com, self.handle_serial_data)
        # self.RS232Listener.start()

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

    def handle_serial_data(self, data):
        """
        serial data handling for more information visit:
        https://colla.inficon.com/display/VCRD/RS232+Protocoll
        """

        if len(data) > 2:
            print("invalid command, too short")
            return

        command_code = data[:2]
        print("command: " + str(command_code))

        writing = False
        if len(data) > 2:
            writing = data[2] == ';'
            print("writing: " + str(writing))

        if command_code == 'AL':  # Analogue range lower
            if writing:
                pass
            else:
                pass

        elif command_code == 'AU':  # Analogue range upper
            if writing:
                pass
            else:
                pass
        elif command_code == 'AA':  # Analogue Autorange
            if writing:
                self.frameAnalogOut.frameVoltageDisplay.check_var.set(data[3:])
            else:
                self.frameAnalogOut.frameVoltageDisplay.check_var.get()
        elif command_code == 'AV':  # Analogue Voltage
            pass
        elif command_code == 'EC':  # Emission current
            if writing:
                pass
            else:
                pass
        elif command_code == 'ME':  # Measurement on/off
            if writing:
                pass
            else:
                pass
        elif command_code == 'VW':  # Get Voltage Wehnelt
            response = self.frameVoltages.uWehnelt.value.get()
        elif command_code == 'VC':  # Get Voltage Cage
            response = self.frameVoltages.uCage.value.get()
        elif command_code == 'VF':  # Get Voltage Faraday
            response = self.frameVoltages.uFaraday.value.get()
        elif command_code == 'VB':  # Get Voltage Bias
            response = self.frameVoltages.uBias.value.get()
        elif command_code == 'VD':  # Get Voltage Deflector
            response = self.frameVoltages.uDeflector.value.get()
        elif command_code == 'IF':  # Get Filament Current
            response = self.frameVoltages.iFil.value.get()
        elif command_code == 'PR':  # Get Pressure
            response = self.framePressure.pressure.get()

        return


if __name__ == "__main__":
    root = MainWindow()
    root.after(500, lambda: root.wm_attributes('-fullscreen', 'true'))
    root.mainloop()
