#!/usr/bin/python3

"""
Controls the beenary's integrated (RFID) reader.Supports different types (abstract base class).
"""

from abc import ABC, abstractmethod
import time
import struct
import serial

from loguru import logger

class IdentityReader(ABC):
    """
    Abstract base class to describe functionality of the beernary's inbuilt ID Reader.
    """

    TIMEOUT     = 1   # abstract constant to define serial read timeout

    @property
    @abstractmethod
    def device_path(self):
        """Abstract property to reflect the path of the reader device (e.g /dev/ttyS0)"""

    @property
    @abstractmethod
    def baud_rate(self):
        """Abstract property to reflect the BAUD rate of the reader device (e.g 9600)"""

    def __init__(self, device_path, baud_rate):
        """Common constructor to initialize the reader (open serial device)."""

        self.device_path = device_path
        self.baud_rate = baud_rate

        self.serial_reader = serial.Serial(self.device_path, self.baud_rate, timeout=self.TIMEOUT)


    @abstractmethod
    def read_rfid(self):
        """
        Abstract method to read an RFID tag from the reader device.

        Important: this method shall not be implemented async!
        """

    @abstractmethod
    def flush_queue(self):
        """
        Abstract method to flush inputs of a reader.
        Triggered to free serial queue while draft is in progress.
        """

class UsbRfidReader(IdentityReader):
    """Represents an USB-based RFID reader with high-level tag read implementation"""

    device_path = str
    baud_rate   = int

    RFID_START  = b"\x04"
    RFID_END    = b"\x02"

    def read_rfid(self):
        """
        Reads an RFID tag from the USB reader.

        Returns: tag ID as bytes[] or None if no data found.
        """

        logger.debug("Trying to read RFID from serial device")

        while True:
            serial_data = self.serial_reader.read(1)
            if serial_data == self.RFID_START:
                logger.debug("RFID start byte detected")
                serial_data = self.serial_reader.read(10)
                logger.info(f"Read RFID tag (id: {serial_data})")
                return serial_data

            elif serial_data == '':
                logger.debug("RFID read timeout/empty data")
            else:
                continue

    def flush_queue(self): # TODO: nest class
        """Flushes inputs of the serial reader."""
        self.serial_reader.reset_input_buffer()

class RawRfidReader(IdentityReader):
    """Represents a serial-based RFID reader with full low-level tag read implementation"""

    device_path = str
    baud_rate   = int

    RFID_START              = b"\x02"
    RFID_END                = b"\x03"

    def read_rfid(self):
        """
        Reads an RFID tag from the USB reader.

        Returns: tag ID as bytes[] or None if no data found.
        """

        logger.debug("Trying to read RFID from serial device")

        while True:
            serial_data = self.serial_reader.read(1)
            logger.trace(f"Received byte: {serial_data}")

            if serial_data == self.RFID_START:
                logger.debug("RFID start byte detected")

                tag_raw         = []                      # raw data bytes as int
                tag_data        = bytes()                 # hex data bytes as string

                for i in range(10):   # read 10 bytes (data)
                    tag_fragment = self.serial_reader.read(1)

                    tag_data += tag_fragment
                    tag_raw.append(int(tag_fragment, 16))

                tag_data = tag_data.decode("ASCII")       # cast hex chars into "real" string

                checksum_raw    = []                      # raw checksum bytes as int

                for i in range(2):   # read 10 bytes (checksum)
                    checksum_fragment = self.serial_reader.read(1)
                    checksum_raw.append(int(checksum_fragment, 16))

                logger.debug(f"Read RFID tag with ID: {tag_data}")

                checksum_data = checksum_raw[0] << 4
                checksum_data = checksum_data | checksum_raw[1]
                logger.debug(f"RFID tag {tag_data} has checksum: {checksum_data}")

                calculated_checksum = self.calculate_checksum(tag_raw)
                logger.debug(f"Calculated RFID tag checksum: {calculated_checksum}")

                if calculated_checksum != checksum_data:
                    logger.error(f"RFID tag {tag_data} checksums do not match")
                else:
                    logger.debug(f"RFID tag {tag_data} checksums match")

                self.flush_queue()
                return tag_data

            elif serial_data == '':
                logger.debug("RFID read timeout/empty data")
            else:
                continue

    def calculate_checksum(self, tag_data):
        """
        Internal method of RawReader to calculate the checksum of the RFID tag.

        Note: this method was written by https://github.com/philippmeisberger/pyrfid/.
        """

        calculated_checksum     = 0

        # Process two characters (one byte) at at time
        for i in range(0, 10, 2):

            # Shift bits 4 (<<) position to have room for next character
            byte = tag_data[i] << 4

            # Combine next character via OR (|) in the previously shifted byte
            byte = byte | tag_data[i+1]

            # Build checksum via XOR (^) between last byte's checksum and current byte
            calculated_checksum = calculated_checksum ^ byte

        return calculated_checksum

    def flush_queue(self):
        """Flushes inputs of the serial reader."""
        self.serial_reader.reset_input_buffer()

class MockRfidReader(IdentityReader):
    """A simple mock for testing without physical rfid sensor."""

    device_path = str
    baud_rate   = int

    RFID_START  = b"\x00"
    RFID_END    = b"\x00"

    def __init__(self, device_path, baud_rate):
        return

    def read_rfid(self):
        time.sleep(10)
        return "42DEADBE"

    def flush_queue(self):
        return
    