import abc
import struct
import logging

from crccheck.crc import Crc

from .constants import *
from .exceptions import *

log = logging.getLogger(__name__)


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

    def __init__(self, int_obj):
        """
        Parameters
        ---------
        int_obj : InterfaceImpl
            An instance of an interface implementation (InterfaceSerial,...).
        """
        log.debug("Instantiating P3")
        self._crccalc = Crc(**CRC_PARAMS)
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
        return self._interface.comm_handle

    @abc.abstractmethod
    def _encode_package(self, cmd, pid, data=None) -> tuple:
        pass

    def _decode_package(self, cmd, pid, data_rcv: bytes) -> bytes:
        """
        Extracts the data from a raw response message.
        Raises exception in case of an incoming error message.

        Parameters
        ----------
        cmd : int
        pid : int
        data_rcv : bytes
            data as received from device

        Returns
        -------
        bytes

        Raises
        ------
        P3DevError:
            - if device returns an error message
        P3CommError:
            - in case of a correspondence mismatch
        """
        log.debug(f"Decode package for cmd: {cmd}, pid: {pid}.")
        dev_id = data_rcv[1]
        if dev_id in self._known_devices:
            self._dev_id = ID(dev_id)
        cmd_rcv = data_rcv[self.POSITION_CMD]
        pid_rcv = data_rcv[self.POSITION_PID: self.POSITION_PID + 2]
        pid_rcv = struct.unpack(">H", pid_rcv)[0]

        comm_ok = (cmd_rcv == cmd + 1) and (pid_rcv == pid)
        dev_error = pid_rcv == 65535

        data = data_rcv[self.POSITION_DATA: -2]
        if dev_error:
            error_code = data[0]
            error_ext = None
            if len(data) == 2:
                error_ext = data[1]
            raise P3DevError(error_code, err_code_ext=error_ext)
        if not comm_ok:
            raise P3CommError(
                "Correspondence mismatch: " "try to run the command again."
            )
        else:
            return data

    def _send_raw(self, comm_handle, data_raw: bytes):
        log.debug("write bytes")
        comm_handle.write(data_raw)

    @abc.abstractmethod
    def _receive_raw(self, comm_handle):
        pass

    def send_receive_data(self, cmd, pid, data=None, timeout=None) -> bytes:
        """
        check data format and send data as bytearray. The protocol P3
        requires the acknowledgement of every command, which is why
        sending and receiving data have to be bundled together

        Parameters
        ----------
        cmd : int
            A decimal integer
        pid : int
            Another decimal integer
        data : tuple[int], list[int]
            tuple or list of 8-bit ints
        timeout : float or None
            communication timeout, can be used for commands that take
            longer to execute.

        Returns
        -------
        bytes
            raw bytestream sent by device

        Raises
        ------
        P3ValueError
            - if passed list contains values larger than 8-bit
            - if input data is too large
        P3CommError
            - if checksum fails, if pid does not match sent pid
        P3DevError
            - if device returns an error
        """
        log.debug("send/receive data")
        timeout_old = self.comm_handle.timeout
        set_timeout = timeout is not None
        if set_timeout:
            log.debug(f"set timeout {timeout}")
            self.comm_handle.timeout = timeout

        pkg_send = bytes(self._encode_package(cmd, pid, data=data))
        with self.comm_handle as com_obj:
            self._send_raw(com_obj, pkg_send)
            pkg_rcv = self._receive_raw(com_obj)

        if set_timeout:
            log.debug(f"reset timeout {timeout}")
            self.comm_handle.timeout = timeout_old
        return self._decode_package(cmd, pid, pkg_rcv)


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

    def __init__(self, interface_obj):
        """
        Parameters
        ---------
        interface_obj: InterfaceImpl
        """
        super().__init__(interface_obj)
        log.debug("Instantiating P3V0")
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
        log.debug(f"Encode package for cmd: {cmd}, pid: {pid}.")

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
        log.debug("read bytes")
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
