from serial import Serial
import threading
import time


def handle_serial_data(self,
                       data) -> None | str:
    """
    serial data handling for more information visit:
    https://colla.inficon.com/display/VCRD/RS232+Protocoll
    """
    while data.endswith(b'\r') or data.endswith(b'\n'):
        data = data[:len(data) - 1]
    response = data + b'\r\n'

    if len(data) < 2:
        return response + b'Error, cmd too short\r\n'

    command_code = data[:2]
    print("command: " + str(command_code))

    writing = False
    value = None
    if len(data) > 2:
        writing = data[2:3] == b';'
        if not writing:
            return response + b'cmd too long or invalid writing operator\r\n'
        value = data[3:].decode()

    if command_code == b'AL':  # Analogue range lower
        if writing:
            if 'E-' in value:
                try:
                    self.content_frame.pages["Setting"].entryLower.set(value)
                    self.set_range()
                except ValueError:
                    response += b'value Error'
            else:
                response += b'missing [E-]'
        else:
            response += str(self.lowerRange).encode()
    elif command_code == b'AU':  # Analogue range upper
        if writing:
            if 'E-' in value:
                try:
                    self.content_frame.pages["Setting"].entryUpper.set(value)
                    self.set_range()
                except ValueError:
                    response += b'value Error'
            else:
                response += b'missing [E-]'
        else:
            response += str(self.upperRange).encode()
    elif command_code == b'AV':  # Analogue Voltage
        response += str(self.uOut).encode()
    elif command_code == b'EC':  # Emission current
        if writing:
            self.content_frame.pages["Home"].entryEmission.delete(0, ctk.END)
            self.content_frame.pages["Home"].entryEmission.insert(0, value)
            answ = self.set_emission_curr()
            if answ is not None:
                response += answ
        else:
            response += str(self.content_frame.pages["Home"].entryEmission.get()).encode()
    elif command_code == b'ME':  # Measurement on/off
        if writing:
            if value == "1":
                if not self.running:
                    self.switch_event()
            else:
                if self.running:
                    self.switch_event()
        else:
            response += self.running
    elif command_code == b'VW':  # Get Voltage Wehnelt
        response += str(self.content_frame.pages["Home"].Voltages["Wehnelt"].value.get()).encode()
    elif command_code == b'VC':  # Get Voltage Cage
        response += str(self.content_frame.pages["Home"].Voltages["Cage"].value.get()).encode()
    elif command_code == b'VF':  # Get Voltage Faraday
        response += str(self.content_frame.pages["Home"].Voltages["Faraday"].value.get()).encode()
    elif command_code == b'VB':  # Get Voltage Bias
        response += str(self.content_frame.pages["Home"].Voltages["Bias"].value.get()).encode()
    elif command_code == b'VD':  # Get Voltage Deflector
        response += str(self.content_frame.pages["Home"].Voltages["Deflector"].value.get()).encode()
    elif command_code == b'IF':  # Get Filament Current
        response += str(self.content_frame.pages["Home"].Voltages["Current"].value.get()).encode()
    elif command_code == b'PR':  # Get Pressure
        response += str(self.content_frame.pages["Home"].pressure.get()).encode()
    else:
        response += b'unknown command'

    if response.endswith(b'\r\n'):
        return response
    else:
        return response + b'\r\n'


class RS232Communication(Serial):
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
        Initialize the serial listener with the given RS232 communication interface and callback function.
        """
        super().__init__()
        self.com = com
        self.callback = callback
        self.timeout = timeout
        self.running = True

    def run(self) -> None:
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
                # print("no data")
            else:
                time.sleep(0.1)  # Sleep for 100ms before checking again

    def stop(self) -> None:
        """
        Stop the listener thread.
        """
        self.running = False

    def read_command(self) -> None | bytes:
        """
        Reads Data from the RS232 serial Interface
        :return: returns read bytes or None on timeout
        """
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
