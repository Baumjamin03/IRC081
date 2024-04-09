# AD5280 DigiPot class file

try:
    import smbus
except:
    import smbus2 as smbus


class AD5280:
    def __init__(self, bus_number=1, address=0x2C):
        self.bus = smbus.SMBus(bus_number)
        self.address = address

    def set_potentiometer(self, value):
        if value > 255:
            value = 255
        if value < 0:
            value = 0
        # Write to the digital potentiometer
        self.bus.write_i2c_block_data(self.address, 0x00, [value])

    def read_pot(self):
        # Read the current value of the digital potentiometer
        data = self.bus.read_i2c_block_data(self.address, 0x00, 1)
        return data[0]
