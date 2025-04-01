import asyncio
import struct
import time
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

from .P3Interface import P3V0
from serial import Serial

class ControlGauge(Serial):
    def __init__(self, port, baudrate=57600):
        """
        IRG080 has a measurment range of below 1e-4 mbar and can be damaged by overpressure.
        """
        super().__init__(port, baudrate, timeout=0.5)
        self.p3 = P3V0(self, None, role='master')

        self.pressure = 0
        self.active = False

        self.executor = ThreadPoolExecutor()
        self.loop = asyncio.new_event_loop()

        self.startup_monitoring_thread()

    def read_pid(self, pid):
        """
        Reads the data from the gauge.
        :param pid: pid number
        :return: pid data
        """
        return self.p3.send_receive_data(1, pid)

    def write_pid(self, pid, data):
        """
        Writes the data to the gauge.
        :param pid: pid number
        :param data: pid data to be written
        :return: response data
        """
        return self.p3.send_receive_data(3, pid, data)


    def read_press_unit(self):
        """
        Reads the data unit from trigon.
        0: mbar, 1: Torr, 2: Pa, 3: Micron, 4: Counts, 5: hpa
        :return: data unit string
        """
        unit = struct.unpack('B', self.read_pid(224))[0]
        unit_map = {
            0: "mbar",
            1: "Torr",
            2: "Pa",
            3: "Micron",
            4: "Counts",
            5: "hpa"
        }
        return unit_map.get(unit, "unknown")

    def read_pressure_mbar(self):
        """
        reads the pressure from the gauge and converts it to mbar
        :return: pressure in mbar
        """
        pressure = struct.unpack('>f', self.read_pid(222))[0]
        unit = self.read_press_unit()

        if unit == "Torr":
            pressure *= 1.33322
        elif unit == "Pa":
            pressure /= 100
        elif unit == "Micron":
            pressure *= 0.00133322
        elif unit == "Counts":
            pressure = pressure  # Assuming Counts is already in mbar
        elif unit == "hpa":
            pressure *= 1.0  # Assuming hpa is already in mbar

        return pressure

    def get_pressure(self):
        """
        gets the pressure from the gauge
        :return: pressure in mbar
        """
        return self.pressure

    async def monitor_gauge(self):
        while True:
            try:
                while self.active:
                    try:
                        self.pressure = await self.read_pressure_mbar()
                    except Exception as e:
                        print("monitor error: " + str(e))
                        time.sleep(0.1)
            except Exception as e:
                print("control gauge error: " + str(e))
                time.sleep(0.1)
            finally:
                await asyncio.sleep(0.1)

    def startup_monitoring_thread(self):
        self.active = True
        def run_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        loop_thread = Thread(target=run_loop, daemon=True)
        loop_thread.start()
        asyncio.run_coroutine_threadsafe(self.monitor_gauge(), self.loop)

    def stop_monitoring_thread(self):
        self.active = False

    def resume_monitoring_thread(self):
        self.active = True

if __name__ == "__main__":
    gauge = ControlGauge("COM1")
    print("start")
    while True:
        try:
            print(gauge.read_pressure_mbar())
            time.sleep(0.01)
        except Exception as e:
            print("error: " + str(e))
            time.sleep(0.1)
