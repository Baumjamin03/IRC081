# AD5280 DigiPot class file

from smbus2 import SMBus


class AD5280:
    def __init__(self, i2c_bus, address):
        self.bus = SMBus(i2c_bus)
        self.address = address

    def set_potentiometer(self, value):
        """
        Sets the resistance value of the digipot.
        :param value: Value between 0 and 255.
        """
        if value < 0 or value > 255:
            raise ValueError("Value out of range. Must be between 0 and 255.")

        # The 9th bit is the R/W bit, which is 0 for write.
        data = (self.address << 1) | 0  # Constructing the 7-bit I2C address with the R/W bit set to 0
        self.bus.write_byte_data(data, 0x00, value)  # 0x00 is the command byte for setting the resistance value

    def get_potentiometer(self):
        """
        Reads the resistance value of the digipot.
        :return: Value between 0 and 255.
        """
        # The 9th bit is the R/W bit, which is 1 for read.
        data = (self.address << 1) | 1  # Constructing the 7-bit I2C address with the R/W bit set to 1
        return self.bus.read_byte_data(data, 0x00)  # 0x00 is the command byte for reading the resistance value


# Example usage:
if __name__ == "__main__":
    # Initialize the digipot object with the I2C bus and address
    digipot = AD5280(1, 0b0101100)

    # Set the resistance value to 127
    digipot.set_potentiometer(127)

    # Read the resistance value
    resistance_value = digipot.get_potentiometer()
    print("Resistance value:", resistance_value)
