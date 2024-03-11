# Backend File for IRC081 raspi extension
from mccDAQ.usb_2400 import *


class IRC081(usb_2408_2AO):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except OSError as e:
            print("no, " + str(e))
            return
        print("daq ume")
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

        self.mode = self.SINGLE_ENDED
        self.gain = self.BP_10V
        self.rate = self.HZ25

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
        data, flags = self.AIn(channel, self.mode, self.gain, self.rate)
        data = int(data * self.Cal[self.gain].slope + self.Cal[self.gain].intercept)
        print('Channel %2i = %#x  Volts = %lf' % (channel, data, self.volts(self.gain, data)))
        return self.volts(self.gain, data)


if __name__ == "__main__":
    irc081 = IRC081()
    print(irc081.getSerialNumber())
    # irc081.get_all_voltages()
