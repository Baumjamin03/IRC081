# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:55:21 2024

@author: benj002
"""

import atexit
from SubFrame import *
from IRC081 import IRC081
from decimal import *
from RS232 import *
from DigiPot import AD5280


class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        """
        Initializes the IRUI081 for the IRC081 controller
        """
        super().__init__(*args, **kwargs)

        self.configure(fg_color="black")

        self.irc081 = None
        while self.irc081 is None:
            try:
                self.irc081 = IRC081()
            except Exception as e:
                print("no IRC081 found, Error: " + str(e))
                time.sleep(2)

        atexit.register(self.shutdown)
        self.dPot = None
        try:
            self.dPot = AD5280()
        except Exception as e:
            print(e)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.frameDaq = DaqFrame(self)
        self.frameAnalogOut = AnalogFrame(self)
        self.frameEmission = EmissionFrame(self)
        self.framePressure = PressureFrame(self)
        self.frameVoltages = VoltagesFrame(self)

        self.upperRange = None
        self.lowerRange = None

        self.com = None
        while self.com is None:
            try:
                self.com = RS232Communication()
                self.com.open_port()
            except Exception as e:
                print(e)
                time.sleep(1)
        self.RS232Listener = SerialListener(self.com, self.handle_serial_data)
        self.RS232Listener.start()

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
            self.update_digipot()
            self.after(1000, self.measurement_loop)

    def set_emission_curr(self):
        """
        Sets the Emission current for the IRG080.
        """
        current = self.frameEmission.entryCurrent.get()
        print("i emission set: " + current)
        try:
            self.irc081.set_emission(Decimal(current))
        except DecimalException as e:
            print(str(e))
            return "invalid value"
        return None

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
        if data.endswith(b'\r') or data.endswith(b'\n'):
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
                        factor, exp = value.split('E-')
                        self.frameAnalogOut.entryLowerRange.entry.delete(0, ctk.END)
                        self.frameAnalogOut.entryLowerRange.entry.insert(0, factor)
                        self.frameAnalogOut.entryLowerRange.expEntry.delete(0, ctk.END)
                        self.frameAnalogOut.entryLowerRange.expEntry.insert(0, exp)
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
                        factor, exp = value.split('E-')
                        self.frameAnalogOut.entryUpperRange.entry.delete(0, ctk.END)
                        self.frameAnalogOut.entryUpperRange.entry.insert(0, factor)
                        self.frameAnalogOut.entryUpperRange.expEntry.delete(0, ctk.END)
                        self.frameAnalogOut.entryUpperRange.expEntry.insert(0, exp)
                        self.set_range()
                    except ValueError:
                        response += b'value Error'
                else:
                    response += b'missing [E-]'
            else:
                response += str(self.upperRange).encode()
        elif command_code == b'AA':  # Analogue Autorange
            if writing:
                if value == 1:
                    self.frameDaq.switch_var.set(True)
                else:
                    self.frameDaq.switch_var.set(False)
            else:
                response += str(self.frameAnalogOut.frameVoltageDisplay.check_var.get()).encode()
        elif command_code == b'AV':  # Analogue Voltage
            response += str(self.frameAnalogOut.frameVoltageDisplay.value.get()).encode()
        elif command_code == b'EC':  # Emission current
            if writing:
                self.frameEmission.entryCurrent.delete(0, ctk.END)
                self.frameEmission.entryCurrent.insert(0, value)
                answ = self.set_emission_curr()
                if answ is not None:
                    response += answ
            else:
                response += str(self.frameDaq.emissionDisplay.value.get()).encode()
        elif command_code == b'ME':  # Measurement on/off
            if writing:
                if value == 1:
                    self.frameDaq.switch_var.set("on")
                else:
                    self.frameDaq.switch_var.set("off")
            else:
                response += self.frameDaq.switch_var.get().encode()
        elif command_code == b'VW':  # Get Voltage Wehnelt
            response += str(self.frameVoltages.uWehnelt.value.get()).encode()
        elif command_code == b'VC':  # Get Voltage Cage
            response += str(self.frameVoltages.uCage.value.get()).encode()
        elif command_code == b'VF':  # Get Voltage Faraday
            response += str(self.frameVoltages.uFaraday.value.get()).encode()
        elif command_code == b'VB':  # Get Voltage Bias
            response += str(self.frameVoltages.uBias.value.get()).encode()
        elif command_code == b'VD':  # Get Voltage Deflector
            response += str(self.frameVoltages.uDeflector.value.get()).encode()
        elif command_code == b'IF':  # Get Filament Current
            response += str(self.frameVoltages.iFil.value.get()).encode()
        elif command_code == b'PR':  # Get Pressure
            response += str(self.framePressure.pressure.get()).encode()
        else:
            response += b'unknown command'

        if response.endswith(b'\r\n'):
            return response
        else:
            return response + b'\r\n'

    def update_digipot(self):
        voltage = self.frameAnalogOut.frameVoltageDisplay.value.get()
        d_value = voltage*256//10
        self.dPot.set_potentiometer(d_value)


if __name__ == "__main__":
    root = MainWindow()
    root.after(500, lambda: root.wm_attributes('-fullscreen', 'true'))
    root.mainloop()
