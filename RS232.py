import serial
import threading
import time


class RS232Communication:
    def __init__(self, port='/dev/ttyAMA10', baudrate=9600):
        """
        Initialize the RS232 communication object with the given port and baudrate.
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None

    def open_port(self):
        """
        Open the serial port for communication.
        """
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate)
        except Exception as e:
            print(f"Error opening port: {e}")

    def close_port(self):
        """
        Close the serial port.
        """
        if self.serial_port is not None:
            self.serial_port.close()

    def send_data(self, data):
        """
        Send the given data over the serial port.
        """
        if self.serial_port is not None:
            self.serial_port.write(data.encode())

    def receive_data(self, num_bytes):
        """
        Receive the given number of bytes over the serial port.
        """
        if self.serial_port is not None:
            return self.serial_port.read(num_bytes).decode()

    def get_available_bytes(self):
        """
        Get the number of available bytes to read from the serial port.
        """
        if self.serial_port is not None:
            return self.serial_port.inWaiting()


class SerialListener(threading.Thread):
    def __init__(self, com, callback, timeout=10.0):
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
                data = self.com.receive_data(self.com.get_available_bytes())
                self.callback(data)
            elif time.time() - start_time > self.timeout:
                # Exit the loop if the timeout has been reached
                break
            else:
                time.sleep(0.1)  # Sleep for 100ms before checking again

    def stop(self):
        """
        Stop the listener thread.
        """
        self.running = False


class SerialWriter:
    def __init__(self, com):
        """
        Initialize the serial writer with the given RS232 communication object.
        """
        self.com = com

    def write_data(self, data):
        """
        Write the given data to the serial port without blocking the rest of the program.
        """
        if self.com.get_available_bytes() > 0:
            # If the receive-buffer is full, wait until some data is read
            timeout = 5.0  # Timeout in seconds
            start_time = time.time()
            while self.com.get_available_bytes() == 0 and time.time() - start_time < timeout:
                time.sleep(0.1)  # Sleep for 100ms before checking again
        self.com.send_data(data)
