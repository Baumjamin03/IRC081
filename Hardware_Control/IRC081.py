# Backend File for IRC081 raspi extension
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

from Hardware_Control.usb_2400 import *  # https://github.com/wjasper/Linux_Drivers/tree/master/USB
from decimal import *
import asyncio
import configparser

RESISTOR1G11 = Decimal("1.11E9")  # ohm
RESISTOR1G02 = Decimal("1.02E9")
DECIMAL_1E11 = Decimal("1e-11")
DECIMAL_2E5 = Decimal("2e-5")
DECIMAL_1_98E5 = Decimal("1.98e-5")
D10d1 = Decimal(10.1)
D51 = Decimal(51)

SENSITIVITY = Decimal(29)  # 1/mbar


class IRC081(usb_2408_2AO):
    def __init__(self, *args, **kwargs):
        """
        Initializes the IRC081 controller.
        """
        super().__init__(*args, **kwargs)

        getcontext().prec = 15

        self.executor = ThreadPoolExecutor()

        self.loop = asyncio.new_event_loop()

        self.measMode = self.SINGLE_ENDED
        self.measGain = self.BP_10V
        self.measRate = self.HZ25

        self.set_filament_current_limitation(2)

        self.factors = get_calibration_values(self.getSerialNumber())
        self.aInput = []

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
        self.uEmission = 0

        self.iFaraday = 0
        self.iCage = 0
        self.iFil = 0
        self.iCollector = 0
        self.iEmission = 0

        self.setEmission = 0
        self.pressure = 0
        self.transmission = 0

        self.dOut = 0

    def start_refresh_thread(self):
        def run_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        loop_thread = Thread(target=run_loop, daemon=True)
        loop_thread.start()
        asyncio.run_coroutine_threadsafe(self.refresh_controller_data(), self.loop)

    async def refresh_controller_data(self):
        """
        Reads and Calculates measurement Data
        """
        while not False:
            try:
                await self.read_analogue_inputs()

                self.uDeflector = self.aInput[0] * D10d1 * self.factors["Factor AI0"]
                self.uWehnelt = self.aInput[1] * D10d1 * self.factors["Factor AI1"]
                self.uCage = self.aInput[2] * D51 * self.factors["Factor AI2"]
                self.uFaraday = self.aInput[3] * D51 * self.factors["Factor AI3"]
                self.uBias = self.aInput[5] * D10d1 * self.factors["Factor AI5"]
                self.iFil = self.aInput[6] * self.factors["Factor AI6"]

                self.iCollector = await self.compute_ion_current()
                self.iEmission = self.compute_emission_curr()
                self.uEmission = await self.set_emission_prop()
                self.pressure = self.calculate_pressure_mbar()

                self.iFaraday = await self.read_faraday_current()
                self.iCage = self.read_cage_current()
                self.transmission = (self.get_faraday_current() / self.get_emission_current()) * 100

                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"Error in refresh_controller_data: {e}")
                await asyncio.sleep(1)

    async def read_analogue_inputs(self):
        for i in range(16):
            self.aInput[i] = await self.async_get_voltage(i)
            await asyncio.sleep(0.01)

    def calculate_pressure_mbar(self):
        """
        Calculates the pressure from the ion current, emission current and sensitivity factor.
        """
        ion_curr = self.get_ion_current()
        emission_curr = self.get_emission_current()
        pressure = Decimal(ion_curr / (SENSITIVITY * emission_curr))
        return pressure

    async def set_emission_current_should_100u(self, i_e_should):
        """
        Sets emission current in the 100uA range.
        """
        i_e_should = Decimal(i_e_should * Decimal("1e-6"))
        bias_voltage = self.get_voltage_bias()
        value = ((i_e_should - (bias_voltage / RESISTOR1G11)) * (10 ** 5)) / self.factors["Factor I Emission0"]
        self.bitE = 1
        await self.update_digital_output()
        self.AOut(1, float(value))
        return value

    async def set_emission_current_should_1m(self, i_e_should):
        """
        Sets emission current in the 1mA range.
        """
        i_e_should = Decimal(i_e_should * Decimal("1e-6"))
        bias_voltage = self.get_voltage_bias()
        value = ((i_e_should - (bias_voltage / RESISTOR1G11)) * (10 ** 4)) / self.factors["Factor I Emission1"]
        self.bitE = 0
        await self.update_digital_output()
        self.AOut(1, float(value))
        return value

    def set_emission(self, curr: Decimal):
        """
        Sets the emission current property
        """
        self.setEmission = curr

    async def set_emission_prop(self):
        """
        Calculates and sets the voltage level corresponding to the set emission current.
        Returns voltage level
        """
        current = self.setEmission
        if (current == 0) or (current is None) or (current == ""):
            current = Decimal(30)
        emission_current = Decimal(current)
        voltage = 0
        if emission_current < 100:
            voltage = await self.set_emission_current_should_100u(emission_current)
        elif emission_current < 1000:
            voltage = await self.set_emission_current_should_1m(emission_current)
        else:
            print("emission current too big")
        return voltage

    def compute_emission_curr(self):
        """
        Reads and calculates actual emission current.
        """
        emission_voltage = self.aInput[13]
        bias_voltage = self.get_voltage_bias()
        if self.bitE == 0:
            value = (emission_voltage * DECIMAL_2E5 * 10 + (bias_voltage / RESISTOR1G11)) * self.factors["Factor I Emission1"]
        else:
            value = (emission_voltage * DECIMAL_2E5 + (bias_voltage / RESISTOR1G11)) * self.factors["Factor I Emission0"]
        return value

    def get_voltage(self, channel: int) -> Decimal:
        """
        Reads and returns voltage of selected analog input channel (0-15).
        """
        data, flags = self.AIn(channel, self.measMode, self.measGain, self.measRate)
        data = int(data * self.Cal[self.measGain].slope + self.Cal[self.measGain].intercept)
        return Decimal(self.volts(self.measGain, data))

    async def async_get_voltage(self, channel):
        """
        Reads and returns voltage of selected analog input channel (0-15) asynchronously.
        """
        return await self.loop.run_in_executor(self.executor, self.get_voltage, channel)

    async def update_digital_output(self):
        """
        Processes the Bits to a HEX-value for the Digital outputs.
        """
        output_value = ((self.bitA << 7) | (self.bitB << 6) | (self.bitC << 5) | (self.bitD << 4) | (self.bitE << 3) |
                        (self.bitF << 2) | (self.bitOn << 1))
        if self.dOut != output_value:
            await self.loop.run_in_executor(self.executor, self.DOut, output_value)
            self.dOut = output_value
        return

    async def set_filament_current_limitation(self, i_fil_max=2):
        """
        Sets maximum heater current, 1V = 1A, max 2 A.
        """
        if i_fil_max > 2:
            i_fil_max = 2
        value = i_fil_max / self.factors["Factor AI6"]
        print("filament_current_limitation: " + str(value))
        await self.loop.run_in_executor(self.executor, self.AOut, (0, float(value)))
        return

    async def read_faraday_current(self):
        """
        Reads and calculates faraday current.
        """
        voltage = self.aInput[11]
        faraday_voltage = self.get_voltage_faraday()
        if self.bitE == 0:
            value = (voltage * DECIMAL_1_98E5 * 10 - (faraday_voltage / RESISTOR1G02)) * self.factors["Factor I Faraday1"]
        else:
            value = (voltage * DECIMAL_1_98E5 - (faraday_voltage / RESISTOR1G02)) * self.factors["Factor I Faraday0"]
        return value

    async def read_cage_current(self):
        """
        Reads and calculates cage current.
        """
        voltage = self.aInput[10]
        cage_voltage = self.get_voltage_cage()
        if self.bitE == 0:
            value = (voltage * DECIMAL_1_98E5 * 10 - (cage_voltage / RESISTOR1G02)) * self.factors["Factor I Cage1"]
        else:
            value = (voltage * DECIMAL_1_98E5 - (cage_voltage / RESISTOR1G02)) * self.factors["Factor I Cage0"]
        return value

    async def compute_ion_current(self):
        """
        Reads and calculates ion current respective to the range.
        """
        voltage = self.aInput[15]
        current = Decimal(voltage) * DECIMAL_1E11 * (10 ** (6 - self.ionRange)) * self.factors[
            f"Factor I Ion{6 - self.ionRange}"]

        if (voltage > 4.5) and (self.ionRange > 0):
            self.ionRange = self.ionRange - 1
            await self.ion_range_handler()
        elif (voltage < 0.4) and (self.ionRange < 6):
            self.ionRange = self.ionRange + 1
            await self.ion_range_handler()
        return current

    async def ion_range_handler(self):
        """
        Processes the Range to set the respective bits.
        """
        coll_range = self.ionRange
        self.bitC = 1 - coll_range // 4
        coll_range = coll_range % 4
        self.bitB = 1 - coll_range // 2
        coll_range = coll_range % 2
        self.bitA = 1 - coll_range
        await self.update_digital_output()
        print("new range: " + str(self.ionRange))
        print("A: " + str(self.bitA) + " B: " + str(self.bitB) + " C: " + str(self.bitC))
        return

    def measurement_start(self):
        """
        Sets the Voltages for the IRG080 configured by the potentiometers on the IRC081.
        """
        print("start")
        print("interlock < 2.5V = good: " + str(self.get_voltage(4)))
        self.bitOn = 1
        self.update_digital_output()

    def measurement_end(self):
        """
        Resets IRC081 digital outputs and emission current.
        """
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
        return self.aInput[15]

    def get_emission_current(self):
        return self.iEmission

    def get_emission_voltage(self):
        return self.uEmission

    def get_transmission(self):
        return self.transmission

    def get_faraday_current(self):
        return self.iFaraday

    def get_cage_current(self):
        return self.iCage


def get_calibration_values(serial_number) -> dict[str, Decimal]:
    """
    Inserts the calibration values by serial number into a dictionary and returns it
    """
    calibration_file = configparser.ConfigParser()
    calibration_file.read('Assets/IRC081 Calibration.ini')
    output_dict = {}
    for key in calibration_file[serial_number]:
        key_value = calibration_file[serial_number][key]
        try:
            output_dict[key] = Decimal(key_value)
        except Exception as e:
            print(f"Error in get_calibration_values: {e}")
            output_dict[key] = 0
    return output_dict
