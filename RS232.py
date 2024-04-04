import serial
import threading
import time
from array import *


class RS232Communication(serial.Serial):
    def __init__(self, port='/dev/ttyAMA10', baudrate=9600):
        """
        Initialize the RS232 communication object with the given port and baudrate.
        """
        super().__init__(port, baudrate)

    def open_port(self):
        """
        Open the serial port for communication.
        """
        try:
            self.open()
        except Exception as e:
            print(f"Error opening port: {e}")

    def close_port(self):
        """
        Close the serial port.
        """
        if self is not None:
            self.close()

    def receive_data(self, num_bytes):
        """
        Receive the given number of bytes over the serial port.
        """
        if self is not None:
            sauce = self.read(num_bytes)
            print(sauce)
            return sauce.decode()

    def get_available_bytes(self):
        """
        Get the number of available bytes to read from the serial port.
        """
        if self is not None:
            return self.in_waiting


class SerialListener(threading.Thread):
    def __init__(self, com, callback, timeout=5.0):
        """
        Initialize the serial listener with the given RS232 communication object and callback function.
        """
        super().__init__()
        self.com = com
        self.callback = callback
        self.timeout = timeout
        self.running = True

    def run(self):
        """
        Run the listener thread.
        """
        start_time = time.time()
        while self.running:
            if self.com.get_available_bytes() > 0:
                start_time = time.time()
                received_data = self.read_command()
                self.com.write(self.callback(received_data))
            elif time.time() - start_time > self.timeout:
                # Exit the loop if the timeout has been reached
                start_time = time.time()
                print("no data")
            else:
                time.sleep(0.1)  # Sleep for 100ms before checking again

    def stop(self):
        """
        Stop the listener thread.
        """
        self.running = False

    def read_command(self):
        received_data = b''
        start_time = time.time()
        while True:
            if self.com.get_available_bytes() > 0:
                received_data += self.com.read(1)
                if received_data.endswith(b'\n') or received_data.endswith(b'\r'):
                    print(received_data)
                    return received_data
            else:
                time.sleep(0.05)

            if time.time() - start_time > 5:
                print("timeout, no termination character received")
                return None
