#!/usr/bin/python3

"""
Controls the beenary's integrated valve. Currently only supports basic GPIO lock/unlock.
"""

try:
    import RPi.GPIO as GPIO
except: # pylint: disable=bare-except
    import Mock.GPIO as GPIO

class Valve:
    """Represents a binary valve based on GPIO output."""

    gpio_pin:  int   # attribute to reflect GPIO pin of valve

    def __init__(self, gpio_pin, unlocked=False):
        """
        Constructor to initialize the valve.

        Parameters:
        gpio_pin - GPIO pin of the valve to lock/unlock
        locked   - (Optional) initial state for valve (locked/unlocked)
        """
        self.gpio_pin = gpio_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)

        self.unlocked = unlocked

    @property
    def unlocked(self):
        """Handles the valve's state (locked/unlocked)"""
        return self.unlocked

    @unlocked.setter
    def unlocked(self, value):
        GPIO.output(self.gpio_pin, value)

    def close(self):
        """Method to close the valve connection."""
        self.unlocked = False
        GPIO.cleanup()
