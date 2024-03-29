#!/usr/bin/python3

"""
Controls the beenary's integrated signaling light. Currently https://www.adafruit.com/product/5125.
"""

from abc import ABC, abstractmethod

import serial
import time

class SignalLight(ABC):
    """Abstract base class to describe functionality of the signal light."""

    @abstractmethod
    def __init__(self, device_path: str, baud_rate: int):
        """Abstract constructor to initialize the beer flow sensors."""

    @abstractmethod
    def send_command(self, cmd: hex):
        """
        Abstract method to add a pulse to the flow counter.

        Parameters:
        pulses - amount of pulses to add to the current value
        """

class BeernarySignalLight(SignalLight):
    """
    Represents the integrated traffic light. See https://www.adafruit.com/product/5125.
    """

    TIMEOUT     = 1

    RED_ON = 0x11
    RED_OFF = 0x21
    RED_BLINK = 0x41

    YELLOW_ON= 0x12
    YELLOW_OFF = 0x22
    YELLOW_BLINK = 0x42

    GREEN_ON = 0x14
    GREEN_OFF = 0x24
    GREEN_BLINK = 0x44

    BUZZER_ON = 0x18
    BUZZER_OFF = 0x28
    BUZZER_BLINK = 0x48

    def __init__(self, device_path, baud_rate):
        """Common constructor to initialize the reader (open serial device)."""

        self.device_path = device_path
        self.baud_rate = baud_rate

        self.serial_device = serial.Serial(self.device_path, self.baud_rate, timeout=self.TIMEOUT)

    def send_command(self, cmd):
        """Sends a command to the serial port."""
        self.serial_device.write(bytes([cmd]))
        time.sleep(0.1)

class BeernarySignalLightMock(SignalLight):
    """A simple mock for testing without signal light."""

    TIMEOUT     = 1

    RED_ON = 0x11
    RED_OFF = 0x21
    RED_BLINK = 0x41

    YELLOW_ON= 0x12
    YELLOW_OFF = 0x22
    YELLOW_BLINK = 0x42

    GREEN_ON = 0x14
    GREEN_OFF = 0x24
    GREEN_BLINK = 0x44

    BUZZER_ON = 0x18
    BUZZER_OFF = 0x28
    BUZZER_BLINK = 0x48

    def __init__(self, device_path, baud_rate):
        return

    def send_command(self, cmd):
        return
