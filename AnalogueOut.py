# AD5280 DigiPot class file

import smbus2 as smbus


class MCP4725:
    def __init__(self,
                 bus_number: int = 1,
                 address: int = 0x60):
        self.bus = smbus.SMBus(bus_number)
        self.address = address

    def set_analogue_out(self, value: int):
        """

        :param value: 12 bit value for the DAC
        :return: None
        """
        # Constrain the value to 12-bit range (0 - 4095)
        value = max(0, min(4095, value))

        # Prepare MSB and LSB for the 12-bit DAC value
        v_msb = (value >> 4) & 0xFF  # Upper 8 bits (4 bits are actual data)
        v_lsb = (value & 0x0F) << 4  # Lower 4 bits shifted into position

        bytes_register = 0x40
        bytes_v = [v_msb, v_lsb]

        # Write the byte sequence to the MCP4725
        self.bus.write_i2c_block_data(self.address, bytes_register, bytes_v)


