# Backend File for IRC081 raspi extension
from mccDAQ.usb_2400 import *  # https://github.com/wjasper/Linux_Drivers/tree/master/USB
from GetCalibrationValues import *
from decimal import *

RESISTOR1G11 = Decimal("1.11E9")


class IRC081(usb_2408_2AO):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except OSError as e:
            print("no, " + str(e))
            return
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

        getcontext().prec = 15

        self.measMode = self.SINGLE_ENDED
        self.measGain = self.BP_10V
        self.measRate = self.HZ25

        self.config_corr_factors()

        self.sensitivity = Decimal(29)

        self.set_filament_current_limitation(2)  # 2V = 2A

        self.bitA = 1
        self.bitB = 1
        self.bitC = 1
        self.bitD = 0
        self.bitE = 0
        self.bitF = 0
        self.bitOn = 0

        self.ionRange = 0

    def update_digital_output(self):
        output_value = ((self.bitA << 7) | (self.bitB << 6) | (self.bitC << 5) | (self.bitD << 4) | (self.bitE << 3) |
                        (self.bitF << 2) | (self.bitOn << 1))
        print("digital output: " + str(output_value))
        self.DOut(output_value)
        return

    def ion_range_handler(self):
        coll_range = self.ionRange
        self.bitC = 1 - coll_range // 4
        coll_range = coll_range % 4
        self.bitB = 1 - coll_range // 2
        coll_range = coll_range % 2
        self.bitA = 1 - coll_range
        self.update_digital_output()
        print(self.ionRange)
        return

    def get_pressure_mbar(self):
        ion_current = self.get_ion_current()
        emission_current = self.get_emission_curr()

        pressure = ion_current / (self.sensitivity * emission_current)

        return pressure

    def set_emission_curr(self, current):
        if (current == 0) or (current is None) or (current is ""):
            current = 30

        emission_current = Decimal(current)
        if emission_current < 100:
            self.set_emission_current_should_100u(emission_current)
        elif emission_current < 1000:
            self.set_emission_current_should_1m(emission_current)
        else:
            print("current too big")
        return

    def get_voltage_wehnelt(self):
        value = Decimal(self.get_voltage(1)) * Decimal(10.1) * self.factorAI1
        #        print("Wehnelt: " + str(value))
        return "{:.3f}".format(value)

    def get_voltage_deflector(self):
        value = Decimal(self.get_voltage(0)) * Decimal(10.1) * self.factorAI0
        #        print("Deflector: " + str(value))
        return "{:.3f}".format(value)

    def get_voltage_cage(self):
        value = Decimal(self.get_voltage(2)) * Decimal(51) * self.factorAI2
        #        print("Cage: " + str(value))
        return "{:.3f}".format(value)

    def get_voltage_faraday(self):
        value = Decimal(self.get_voltage(3)) * Decimal(51) * self.factorAI3
        #        print("Faraday: " + str(value))
        return "{:.3f}".format(value)

    def get_voltage_bias(self):
        value = Decimal(self.get_voltage(5)) * Decimal(10.1) * self.factorAI5
        #        print("bias: " + str(value))
        return value

    def get_current_filament(self):
        value = Decimal(self.get_voltage(6)) * self.factorAI6
        #        print("filament: " + str(value))
        return "{:.3f}".format(value)

    def get_emission_curr(self):
        voltage = self.get_voltage(13)
        u_bias = self.get_voltage_bias()

        if self.bitD == 1:
            value = (Decimal(voltage) * Decimal("2e-5") * 10 + (u_bias / RESISTOR1G11)) * self.factorIEmission1
        else:
            value = (Decimal(voltage) * Decimal("2e-5") + (u_bias / RESISTOR1G11)) * self.factorIEmission0

        print("emission ist: " + str(value))
        return value

    def get_ion_current(self):
        voltage = self.get_voltage(15)
        current = 0

        if self.ionRange == 0:
            current = self.get_current_ion_50u(voltage)
        elif self.ionRange == 1:
            current = self.get_current_ion_5u(voltage)
        elif self.ionRange == 2:
            current = self.get_current_ion_500n(voltage)
        elif self.ionRange == 3:
            current = self.get_current_ion_50n(voltage)
        elif self.ionRange == 4:
            current = self.get_current_ion_5n(voltage)
        elif self.ionRange == 5:
            current = self.get_current_ion_500p(voltage)
        elif self.ionRange == 6:
            current = self.get_current_ion_50p(voltage)

        if (voltage > 4.5) and (self.ionRange > 0):
            self.ionRange = self.ionRange - 1
            self.ion_range_handler()
        elif (voltage < 0.4) and (self.ionRange < 6):
            self.ionRange = self.ionRange + 1
            self.ion_range_handler()

        print("ion range: " + str(self.ionRange))
        print("ion volts: " + str(voltage))
        print("ion: " + str(current))

        return current

    def get_current_ion_50p(self, voltage):
        value = Decimal(voltage) * Decimal("1e-11") * Decimal("1e0") * self.factorIIon0
        #        print("current_ion_50pA: " + str(value))
        return value

    def get_current_ion_500p(self, voltage):
        value = Decimal(voltage) * Decimal("1e-11") * Decimal("1e1") * self.factorIIon1
        #        print("current_ion_50uA: " + str(value))
        return value

    def get_current_ion_5n(self, voltage):
        value = Decimal(voltage) * Decimal("1e-11") * Decimal("1e2") * self.factorIIon2
        #        print("current_ion_50uA: " + str(value))
        return value

    def get_current_ion_50n(self, voltage):
        value = Decimal(voltage) * Decimal("1e-11") * Decimal("1e3") * self.factorIIon3
        #        print("current_ion_50uA: " + str(value))
        return value

    def get_current_ion_500n(self, voltage):
        value = Decimal(voltage) * Decimal("1e-11") * Decimal("1e4") * self.factorIIon4
        #        print("current_ion_50uA: " + str(value))
        return value

    def get_current_ion_5u(self, voltage):
        value = Decimal(voltage) * Decimal("1e-11") * Decimal("1e5") * self.factorIIon5
        #        print("current_ion_50uA: " + str(value))
        return value

    def get_current_ion_50u(self, voltage):
        value = Decimal(voltage) * Decimal("1e-11") * Decimal("1e6") * self.factorIIon6
        #        print("current_ion_50uA: " + str(value))
        return value

    def set_filament_current_limitation(self, i_fil_max):
        value = i_fil_max / self.factorAI6
        print("filament_current_limitation: " + str(value))
        self.AOut(0, float(value))
        return

    def set_emission_current_should_100u(self, i_e_should):
        i_e_should = Decimal(i_e_should * Decimal("1e-6"))
        voltage_bias = Decimal(self.get_voltage_bias())
        value = ((i_e_should - (voltage_bias / RESISTOR1G11)) * (10 ** 5)) / self.factorIEmission0
        print("emission_current_should 100uA: " + str(value))
        self.bitD = 0
        self.bitE = 0
        self.bitF = 0

        self.update_digital_output()
        self.AOut(1, float(value))
        return

    def set_emission_current_should_1m(self, i_e_should):
        i_e_should = Decimal(i_e_should * Decimal("1e-6"))
        voltage_bias = Decimal(self.get_voltage_bias())
        value = ((i_e_should - (voltage_bias / RESISTOR1G11)) * (10 ** 4)) / self.factorIEmission1
        print("emission_current_should 1mA: " + str(value))
        self.bitD = 0
        self.bitE = 1
        self.bitF = 0

        self.update_digital_output()
        self.AOut(1, float(value))
        return

    def get_voltage(self, channel):
        data, flags = self.AIn(channel, self.measMode, self.measGain, self.measRate)
        data = int(data * self.Cal[self.measGain].slope + self.Cal[self.measGain].intercept)
        #        print('Channel %2i = %#x  Volts = %lf' % (channel, data, self.volts(self.measGain, data)))
        return self.volts(self.measGain, data)

    def measurement_start(self):
        print("start")

        print(self.get_voltage(4))
        print(self.get_voltage(12))

        self.bitOn = 1
        self.update_digital_output()

        return

    def measurement_end(self):
        print("measurement end")
        self.bitOn = 0
        self.update_digital_output()
        self.AOut(1, 0)
        return

    def config_corr_factors(self):
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
        self.factorICage0 = Decimal(factor_array[10])
        self.factorICage1 = Decimal(factor_array[11])
        self.factorIFaraday0 = Decimal(factor_array[12])
        self.factorIFaraday1 = Decimal(factor_array[13])
        self.factorIEmission0 = Decimal(factor_array[14])
        self.factorIEmission1 = Decimal(factor_array[15])
        self.factorIIon0 = Decimal(factor_array[16])
        self.factorIIon1 = Decimal(factor_array[17])
        self.factorIIon2 = Decimal(factor_array[18])
        self.factorIIon3 = Decimal(factor_array[19])
        self.factorIIon4 = Decimal(factor_array[20])
        self.factorIIon5 = Decimal(factor_array[21])
        self.factorIIon6 = Decimal(factor_array[22])
        return
