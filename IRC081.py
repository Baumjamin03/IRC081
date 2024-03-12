# Backend File for IRC081 raspi extension
from mccDAQ.usb_2400 import *
from GetCalibrationValues import *
from decimal import *


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

        self.measMode = self.SINGLE_ENDED
        self.measGain = self.BP_10V
        self.measRate = self.HZ25

        self.config_corr_factors()

    def get_coll_current(self, coll_range):
        volts = self.get_voltage(7)
        c = coll_range // 4
        coll_range = coll_range % 4
        b = coll_range // 2
        coll_range = coll_range % 2
        a = coll_range
        self.DOut(a, 7)
        self.DOut(b, 6)
        self.DOut(c, 5)
        return volts    # scale to current

    def set_emission_curr(self, current):
        pass

    def set_analog_range(self):
        pass

    def get_pressure_mbar(self):
        pass

    def get_pressure_torr(self):
        pass

    def get_voltage_wehnelt(self):
        return self.get_voltage(1)

    def get_voltage_deflector(self):
        return self.get_voltage(0)

    def get_voltage_cage(self):
        return self.get_voltage(3)

    def get_voltage_faraday(self):
        return self.get_voltage(2)

    def get_voltage_fillow(self):
        pass

    def get_voltage_filhigh(self):
        pass

    def get_voltage(self, channel):
        data, flags = self.AIn(channel, self.measMode, self.measGain, self.measRate)
        data = int(data * self.Cal[self.measGain].slope + self.Cal[self.measGain].intercept)
        print('Channel %2i = %#x  Volts = %lf' % (channel, data, self.volts(self.measGain, data)))
        return "{:.3f}".format(self.volts(self.measGain, data))

    def measurement_start(self):
        pass

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
