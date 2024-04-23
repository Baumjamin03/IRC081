# AD5280 DigiPot class file

try:
    import smbus
except:
    import smbus2 as smbus


class MCP4725:
    def __init__(self, bus_number=1, address=0x60):
        self.bus = smbus.SMBus(bus_number)
        self.address = address

    def set_analogue_out(self, value):
        if value > 4095:
            value = 4095
        if value < 0:
            value = 0
        # Write to the digital potentiometer
        self.bus.write_i2c_block_data(self.address, 0x00, [value])
