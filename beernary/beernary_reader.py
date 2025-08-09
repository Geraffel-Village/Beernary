#!/usr/bin/python3

"""
This application provides a local RFID reader via USB.
"""

import modules.reader

RFID_READER = "/dev/ttyUSB0"

if __name__ == "__main__":
    while True:
        reader = modules.reader.UsbRfidReader(RFID_READER, 9600)
        reader.read_rfid()