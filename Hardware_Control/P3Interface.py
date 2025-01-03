import abc
import struct
from serial import Serial
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from crccheck.crc import Crc
from enum import IntEnum

class RS232Communication(Serial):
    def __init__(self, data_callback, port='/dev/ttyAMA10', baudrate=115200):
        """
        Initialize the RS232 communication object with the given port and baudrate.
        """
        super().__init__(port, baudrate, timeout=1)

        self.executor = ThreadPoolExecutor()
        self.loop = asyncio.new_event_loop()
        self.p3 = P3V0(self, data_callback)

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

    def start_listener_thread(self):
        def run_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        loop_thread = Thread(target=run_loop, daemon=True)
        loop_thread.start()
        asyncio.run_coroutine_threadsafe(self.serial_listener_loop(), self.loop)
        print("Listener thread started")

    async def serial_listener_loop(self):
        while True:
            try:
                await asyncio.sleep(0.1)
                if self.in_waiting is not None:
                    if int(self.in_waiting) > 0:
                        print("Data received")
                        try:
                            self.p3.receive_send_data()
                        except Exception as e:
                            print(f"Error reading data: {e}")

            except Exception as e:
                await asyncio.sleep(1)
                print(f"Unexpected Error in listener loop: {e}")

"""
I copied everything below this line, ngl I don't understand it
----------------------------------------------------------------------
"""
class P3ValueError(Exception):
    pass


class P3CommError(Exception):
    pass


class P3DevError(Exception):
    def __init__(self, err_code=0, err_code_ext=0):
        self.err_code = err_code
        self.err_code_ext = err_code_ext


class ADDR(IntEnum):
    RS232 = 0x00
    RS485 = 0x00


class ID(IntEnum):
    NONE = -1
    MASTER = 0x00
    PCG5X0 = 0x02
    MPG5X0 = 0x04
    CDG_STRIPE = 0x06
    BxG5X0 = 0x08
    PXG100 = 0x09
    DDG = 0x0A
    OPG550 = 0x0B
    PSG5X0 = 0x12
    MAG5X0 = 0x14
    CDG_DCI = 0x16
    CDG_SYNE = 0x20


class HEADER_ACK(IntEnum):
    MASTER = 0
    SLAVE = 1


CRC_PARAMS = {
    "width": 16,
    "poly": int(0x1021),
    "initvalue": int(0xFFFF),
    "reflect_input": True,
    "reflect_output": True,
    "xor_output": 0,
}
# ----------------------------------------------------------------------
# Abstract specification of protocol 3
# ----------------------------------------------------------------------
class P3(metaclass=abc.ABCMeta):
    """
    Abstract base class for communication with devices, using the P3
    protocol.
    This is an abstract class and not intended to be used as is.

    Methods to be overwritten in child classes:
        - _encode_package
        - _receive_raw
    """
    PREAMBLE_HEADER_MASTER = ()
    PREAMBLE_HEADER_SLAVE = ()
    MAX_LENGTH_DATA = 0
    MAX_LENGTH_CMF = 0
    MAX_LENGTH_RMF = 0
    POSITION_PID = 0
    POSITION_CMD = 0
    POSITION_DATA = 0

    def __init__(self, int_obj, data_callback=None):
        """
        Parameters
        ---------
        int_obj : InterfaceImpl
            An instance of an interface implementation (InterfaceSerial,...).
        """
        self._crccalc = Crc(**CRC_PARAMS)
        self.data_callback = data_callback
        self._interface = int_obj
        self._protocol_version = None
        self._known_devices = [dev.value for dev in ID]
        self._dev_id = ID.NONE

    @property
    def protocol_version(self):
        return self._protocol_version

    @property
    def device_id(self):
        return self._dev_id

    @property
    def comm_handle(self):
        return self._interface

    @abc.abstractmethod
    def _encode_package(self, cmd, pid, data=None) -> tuple:
        pass

    @staticmethod
    def _send_raw(comm_handle, data_raw: bytes):
        # log.debug("write bytes")
        print("responding with data")
        comm_handle.write(data_raw)

    @abc.abstractmethod
    def _receive_raw(self, comm_handle):
        pass

    def receive_send_data(self):
        # log.debug("receive/send data")
        with self.comm_handle as com_obj:
            pkg_rcv = self._receive_raw(com_obj)
            print("check 3")
            if pkg_rcv:
                cmd = pkg_rcv[self.POSITION_CMD]
                pid = struct.unpack(">H", pkg_rcv[self.POSITION_PID: self.POSITION_PID + 2])[0]
                read_data = pkg_rcv[self.POSITION_DATA: -2]
                print("check 4")
                if read_data:
                    data = self.data_callback(cmd, pid, read_data)

                pkg_send = bytes(self._encode_package(cmd, pid, data=data))
                print("check 5")
                self._send_raw(com_obj, pkg_send)

# ----------------------------------------------------------------------
# Actual implementation of protocol family 3
# ----------------------------------------------------------------------
class P3V0(P3):
    """
    Base class for communication with devices, using P3V0.
    """
    PREAMBLE_HEADER_MASTER = (
        ADDR.RS232.value,
        ID.MASTER.value,
        HEADER_ACK.MASTER.value,
        5,
    )
    PREAMBLE_HEADER_SLAVE = (
        ADDR.RS232.value,
        ID.NONE.value,
        HEADER_ACK.SLAVE.value,
        5,
    )
    MAX_LENGTH_DATA = 250
    MAX_LENGTH_CMF = 261
    MAX_LENGTH_RMF = 261
    POSITION_PID = 5
    POSITION_CMD = 4
    POSITION_DATA = 9

    def __init__(self, interface_obj, data_callback):
        """
        Parameters
        ---------
        interface_obj: InterfaceImpl
        """
        super().__init__(interface_obj, data_callback)
        self._protocol_version = "P3V0"

    def _encode_package(self, cmd, pid, data=None) -> tuple:
        """
        Prepares a data packet to be sent to the device

        Parameters
        ----------
        cmd : int
            A decimal integer
        pid : int
            Another decimal integer
        data : tuple[int], list[int]
            list of ints

        Returns
        -------
        tuple :
            list of ints each representing a byte.
        """

        data = [] if data is None else data
        if len(data) > self.MAX_LENGTH_DATA:
            raise P3ValueError(
                "Input data is too long. P3 allows a"
                f"maximum of {self.MAX_LENGTH_DATA} bytes."
            )
        if len([*filter(lambda x: x >= 256, data)]) > 0:
            raise P3ValueError("At least one entry in list is >256")

        # Header
        pkg_payload = list(self.PREAMBLE_HEADER_MASTER[0:3])

        len_data = self.PREAMBLE_HEADER_MASTER[-1]
        if data is not None:
            len_data += len(data)
        pkg_payload.append(len_data)

        # APDU
        pkg_payload.append(cmd)
        pkg_payload.extend(tuple(struct.pack(">H", pid)))
        pkg_payload.extend(tuple(struct.pack(">H", 0x0000)))

        if data is not None:
            pkg_payload.extend(data)

        # CRC
        chcksum = self._crccalc.calc(pkg_payload)
        pkg_payload.extend(tuple(struct.pack("<H", chcksum)))

        return tuple(pkg_payload)

    def _receive_raw(self, com_obj):
        print("receiving raw data")
        pkg_rcv = b""

        # preamble & header
        header_size = len(self.PREAMBLE_HEADER_MASTER)
        pkg_rcv += com_obj.read(header_size)
        if len(pkg_rcv) < header_size:
            # may happen when running into timeout problems.
            msg = (
                f"header: bytes missing, "
                f"received {len(pkg_rcv)} out of {header_size}."
            )
            raise P3CommError(msg)
        package_size = pkg_rcv[-1]
        print("check 2")
        if self.MAX_LENGTH_RMF < package_size:
            msg = f"data: " f"size of RMF exceeds {self.MAX_LENGTH_RMF} bytes"
            raise P3CommError(msg)

        # APDU
        pkg_rcv += com_obj.read(package_size)

        # CRC
        pkg_rcv += com_obj.read(2)

        # check package integrity
        checksum_rcvd = struct.unpack("<H", pkg_rcv[-2::])[0]
        checksum_calc = self._crccalc.calc(pkg_rcv[0:-2])
        if checksum_rcvd != checksum_calc:
            raise P3CommError("data: Checksum mismatch")

        return pkg_rcv
