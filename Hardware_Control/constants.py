# ----------------------------------------------------------------------
# P3
# ----------------------------------------------------------------------
from enum import IntEnum


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