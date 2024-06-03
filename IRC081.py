# Backend File for IRC081 raspi extension

from mccDAQ.usb_2400 import *  # https://github.com/wjasper/Linux_Drivers/tree/master/USB
from GetCalibrationValues import *
from decimal import *

RESISTOR1G11 = Decimal("1.11E9")  # ohm
SENSITIVITY = 29  # 1/mbar


class IRC081(usb_2408_2AO):
    def __init__(self, *args, **kwargs):
        """
        Initializes the IRC081 controller.
        """
        super().__init__(*args, **kwargs)
        print('wMaxPacketSize =', self.wMaxPacketSize)
        for gain in range(1, 10):
            print('Calibration Table: Range =', gain,
                  'Slope = ', format(self.Cal[gain].slope, '.5f'),
                  'Intercept = ', format(self.Cal[gain].intercept, '5f'))

        if self.productID == 0x00fe:
            print('\nAnalog Out Calibration')
            for chan in range(0, 2):
                print('Calibration Table: Channel =', chan,
                      'Slope = ', format(self.Cal_AO[chan].slope, '.5f'),
                      'Intercept = ', format(self.Cal_AO[chan].intercept, '5f'))
        print('')
        for chan in range(8):
            print('CJC Gradient: Chan =', chan,
                  ' CJC Gradient =', format(self.CJCGradient[chan], '.5f'))
        print('\nMFG Calibration date: ', self.getMFGCAL())

        getcontext().prec = 18
        self.measMode = self.SINGLE_ENDED
        self.measGain = self.BP_10V
        self.measRate = self.HZ25

        factor_array = get_calibration_values(self.getSerialNumber())
        print(factor_array)
        self.factorAI0 = Decimal(factor_array[2])
        self.factorAI1 = Decimal(factor_array[3])
        self.factorAI2 = Decimal(factor_array[4])
        self.factorAI3 = Decimal(factor_array[5])
        self.factorAI5 = Decimal(factor_array[6])
        self.factorAI6 = Decimal(factor_array[7])
        self.factorAI8 = Decimal(factor_array[8])
        self.factorAI9 = Decimal(factor_array[9])
        self.factorIEmission0 = Decimal(factor_array[14])
        self.factorIEmission1 = Decimal(factor_array[15])
        self.factorIIon0 = Decimal(factor_array[16])
        self.factorIIon1 = Decimal(factor_array[17])
        self.factorIIon2 = Decimal(factor_array[18])
        self.factorIIon3 = Decimal(factor_array[19])
        self.factorIIon4 = Decimal(factor_array[20])
        self.factorIIon5 = Decimal(factor_array[21])
        self.factorIIon6 = Decimal(factor_array[22])

        self.sensitivity = Decimal(SENSITIVITY)
        self.set_filament_current_limitation(2)  # 2V = 2A

        self.bitA = 1
        self.bitB = 1
        self.bitC = 1
        self.bitD = 1
        self.bitE = 1
        self.bitF = 1
        self.bitOn = 1
        self.ionRange = 0

        self.uBias = 0
        self.uWehnelt = 0
        self.uDeflector = 0
        self.uFaraday = 0
        self.uCage = 0
        self.iFil = 0
        self.setEmission = 0
        self.iCollector = 0
        self.iEmission = 0
        self.pressure = 0
        self.uEmission = 0
        self.uIon = 0

    def refresh_controller_data(self):
        """
        Reads and Calculates measurement Data.
        """
        self.uBias = Decimal(self.get_voltage(5)) * Decimal(10.1) * self.factorAI5
        self.uWehnelt = Decimal(self.get_voltage(1)) * Decimal(10.1) * self.factorAI1
        self.uDeflector = Decimal(self.get_voltage(0)) * Decimal(10.1) * self.factorAI0
        self.uFaraday = Decimal(self.get_voltage(3)) * Decimal(51) * self.factorAI3
        self.uCage = Decimal(self.get_voltage(2)) * Decimal(51) * self.factorAI2
        self.iFil = Decimal(self.get_voltage(6)) * self.factorAI6
        self.iCollector = self.read_ion_current()
        self.iEmission = self.read_emission_curr()
        self.pressure = self.calculate_pressure_mbar()
        self.uEmission = self.set_emission_prop()
        print("ion: " + "{:.5e}".format(self.iCollector) + ", bias: " + "{:.5f}".format(self.uBias))
        print("iEm: " + "{:.5e}".format(self.iEmission) + ", uEm: " + "{:.5f}".format(self.uEmission))
        print(self.pressure)

    def update_digital_output(self):
        """
        Processes the Bits to a HEX-value for the Digital outputs.
        """
        output_value = ((self.bitA << 7) | (self.bitB << 6) | (self.bitC << 5) | (self.bitD << 4) | (self.bitE << 3) |
                        (self.bitF << 2) | (self.bitOn << 1))
        print("digital output: " + str(output_value))
        self.DOut(output_value)
        return

    def ion_range_handler(self):
        """
        Processes the Range to set the respective bits.
        """
        coll_range = self.ionRange
        self.bitC = 1 - coll_range // 4
        coll_range = coll_range % 4
        self.bitB = 1 - coll_range // 2
        coll_range = coll_range % 2
        self.bitA = 1 - coll_range
        self.update_digital_output()
        print("new range: " + str(self.ionRange))
        print("A: " + str(self.bitA) + " B: " + str(self.bitB) + " C: " + str(self.bitC))
        return

    def calculate_pressure_mbar(self):
        """
        Calculates the pressure from the ion current, emission current and sensitivity factor.
        """
        ion_curr = self.get_ion_current()
        emission_curr = self.get_emission_current()
        pressure = Decimal(ion_curr / (self.sensitivity * emission_curr))
        return pressure

    def set_emission(self, curr: Decimal):
        """
        Sets the emission current property
        """
        self.setEmission = curr

    def set_emission_prop(self):
        """
        Calculates and sets the voltage level corresponding to the set emission current.
        Returns voltage level
        """
        current = self.setEmission
        if (current == 0) or (current is None) or (current is ""):
            current = Decimal(30)
        emission_current = Decimal(current)
        voltage = 0
        if emission_current < 100:
            voltage = self.set_emission_current_should_100u(emission_current)
        elif emission_current < 1000:
            voltage = self.set_emission_current_should_1m(emission_current)
        else:
            print("current too big")
        return voltage


    def read_emission_curr(self):
        """
        Reads and calculates actual emission current.
        """
        emission_voltage = Decimal(self.get_voltage(13))
        bias_voltage = self.get_voltage_bias()
        if self.bitE == 0:
            value = (emission_voltage * Decimal("2e-5") * 10 + (bias_voltage / RESISTOR1G11)) * self.factorIEmission1
        else:
            value = (emission_voltage * Decimal("2e-5") + (bias_voltage / RESISTOR1G11)) * self.factorIEmission0
        # print("emission volt: " + str(emission_voltage))
        # print("emission ist: " + str(value))
        return value

    def read_ion_current(self):
        """
        Reads and calculates ion current respective to the range.
        """
        voltage = self.get_voltage(15)
        self.uIon = voltage
        print("u Ion: {:.5e}".format(voltage) + ", range: " + str(self.ionRange))
        current = 0
        if self.ionRange == 0:
            current = Decimal(voltage) * Decimal("1e-11") * Decimal("1e6") * self.factorIIon6
        elif self.ionRange == 1:
            current = Decimal(voltage) * Decimal("1e-11") * Decimal("1e5") * self.factorIIon5
        elif self.ionRange == 2:
            current = Decimal(voltage) * Decimal("1e-11") * Decimal("1e4") * self.factorIIon4
        elif self.ionRange == 3:
            current = Decimal(voltage) * Decimal("1e-11") * Decimal("1e3") * self.factorIIon3
        elif self.ionRange == 4:
            current = Decimal(voltage) * Decimal("1e-11") * Decimal("1e2") * self.factorIIon2
        elif self.ionRange == 5:
            current = Decimal(voltage) * Decimal("1e-11") * Decimal("1e1") * self.factorIIon1
        elif self.ionRange == 6:
            current = Decimal(voltage) * Decimal("1e-11") * Decimal("1e0") * self.factorIIon0

        if (voltage > 4.5) and (self.ionRange > 0):
            self.ionRange = self.ionRange - 1
            self.ion_range_handler()
        elif (voltage < 0.4) and (self.ionRange < 6):
            self.ionRange = self.ionRange + 1
            self.ion_range_handler()
        # print("ion range: " + str(self.ionRange))
        # print("ion volts: " + str(voltage))
        # print("ion: " + str(current))
        return current

    def set_filament_current_limitation(self, i_fil_max=2):
        """
        Sets maximum heater current, 1V = 1A, max 2 A.
        """
        if i_fil_max > 2:
            i_fil_max = 2
        value = i_fil_max / self.factorAI6
        print("filament_current_limitation: " + str(value))
        self.AOut(0, float(value))
        return

    def set_emission_current_should_100u(self, i_e_should):
        """
        Sets emission current in the 100uA range.
        """
        i_e_should = Decimal(i_e_should * Decimal("1e-6"))
        bias_voltage = self.get_voltage_bias()
        value = ((i_e_should - (bias_voltage / RESISTOR1G11)) * (10 ** 5)) / self.factorIEmission0
        print("emission_current_should 100uA: " + str(value))
        self.bitE = 1
        self.update_digital_output()
        self.AOut(1, float(value))
        return value

    def set_emission_current_should_1m(self, i_e_should):
        """
        Sets emission current in the 1mA range.
        """
        i_e_should = Decimal(i_e_should * Decimal("1e-6"))
        bias_voltage = self.get_voltage_bias()
        value = ((i_e_should - (bias_voltage / RESISTOR1G11)) * (10 ** 4)) / self.factorIEmission1
        print("emission_current_should 1mA: " + str(value))
        self.bitE = 0
        self.update_digital_output()
        self.AOut(1, float(value))
        return value

    def get_voltage(self, channel):
        """
        Reads and return voltage of selected analog input channel (0-15).
        """
        data, flags = self.AIn(channel, self.measMode, self.measGain, self.measRate)
        data = int(data * self.Cal[self.measGain].slope + self.Cal[self.measGain].intercept)
        return self.volts(self.measGain, data)

    def measurement_start(self):
        """
        Sets the Voltages for the IRG080 configured by the potentiometers on the IRC081.
        """
        print("start")
        print("interlock < 2.5V = good: " + str(self.get_voltage(4)))
        self.bitOn = 1
        self.update_digital_output()
        return

    def measurement_end(self):
        """
        Resets IRC081 digital outputs and emission current.
        """
        print("measurement end")
        self.bitA = 1
        self.bitB = 1
        self.bitC = 1
        self.bitD = 1
        self.bitE = 1
        self.bitF = 1
        self.bitOn = 0
        self.update_digital_output()
        self.AOut(1, 0)
        return

    def get_pressure_mbar(self):
        return self.pressure

    def get_voltage_wehnelt(self):
        return self.uWehnelt

    def get_voltage_deflector(self):
        return self.uDeflector

    def get_voltage_cage(self):
        return self.uCage

    def get_voltage_faraday(self):
        return self.uFaraday

    def get_voltage_bias(self):
        return self.uBias

    def get_current_filament(self):
        return self.iFil

    def get_ion_current(self):
        return self.iCollector

    def get_ion_voltage(self):
        return self.uIon

    def get_emission_current(self):
        return self.iEmission

    def get_emission_voltage(self):
        return self.uEmission
