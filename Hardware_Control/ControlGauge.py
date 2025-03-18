from P3Interface import P3V0
from serial import Serial

class ControlGauge(Serial):
    def __init__(self, port, baudrate=9600):
        super().__init__(port, baudrate)
        self.p3 = P3V0(self, None, role='master')

    def read_pid(self, pid):
        return self.p3.send_receive_data(pid, 1)

    def write_pid(self, pid, data):
        return self.p3.send_receive_data(pid, 3, data)
