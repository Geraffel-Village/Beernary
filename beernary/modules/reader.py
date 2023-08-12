#!/usr/bin/python3

"""
Controls the beenary's integrated (RFID) reader.Supports different types (abstract base class).
"""

from abc import ABC, abstractmethod
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

class UsbRfidReader(IdentityReader):
    """Represents an USB-based RFID reader with high-level tag read implementation"""

    device_path : str
    baud_rate   : int

    RFID_START  = "\x04"
    RFID_END    = "\x02"

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

class RawRfidReader(IdentityReader):
    """Represents a serial-based RFID reader with full low-level tag read implementation"""

    device_path = str
    baud_rate   = int

    RFID_START              = 2
    RFID_END                = 3

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

                tag_data = self.serial_reader.read(10)
                logger.debug(f"Read RFID tag (data: {tag_data})")

                checksum_data = self.serial_reader.read(1)
                logger.debug(f"Read RFID tag (checksum: {checksum_data})")
                checksum_data = int(checksum_data, 16)

                self.serial_reader.reset_input_buffer()

                calculated_checksum = self.calculate_checksum(tag_data)
                logger.debug(f"Calculated RFID tag (checksum: {calculated_checksum})")

                if calculated_checksum != checksum_data:
                    logger.error(f"Checksum of RFID tag did not match: {tag_data}")
                else:
                    logger.debug(f"Checksum of RFID tag did match: {tag_data}")

                tag_data = tag_data[1:9].decode('ASCII')

                logger.info(f"Read RFID tag (id: {tag_data})")
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

        calculated_checksum = 0

        # Process two characters (one byte) at at time
        for i in range(0, 10, 2):

            # Shift bits 4 (<<) position to have room for next character
            byte = tag_data[i] << 4

            # Combine next character via OR (|) in the previously shifted byte
            byte = byte | tag_data[i+1]

            # Build checksum via XOR (^) between last byte's checksum and current byte
            calculated_checksum = calculated_checksum ^ byte

        return calculated_checksum
