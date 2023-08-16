#!/usr/bin/python3

"""
Controls the beenary's integrated flowsensor. Currently only pulse-based.
"""

try:
    import RPi.GPIO as GPIO
except: # pylint: disable=bare-except
    import Mock.GPIO as GPIO

class PulseFlowsensor:
    """Represents a flowsensor based on GPIO pulses."""

    pulses: int     # attribute to reflect counted pulses
    gpio_pin: int   # attribute to reflect the used GPIO pin

    def __init__(self, gpio_pin, pulses=0):
        """
        Constructor to initialize the flowsensor.

        Parameters:
        gpio_pin - GPIO pin of the flowsensor to count pulses from
        pulses   - (Optional) start value for pulses to initialize
                   the sensor with. Can be used for recovery purposes
        """
        GPIO.setmode(GPIO.BCM)

        self.pulses     = pulses
        self.gpio_pin   = gpio_pin

        # Add GPIO handling to detect pulses
        GPIO.setup(self.gpio_pin, GPIO.IN)
        GPIO.add_event_detect(self.gpio_pin, GPIO.RISING, callback=self.add_pulse)


    def add_pulse(self, pulses=1):
        """
        Adds one or more pulse counts, mostly used as GPIO callback.

        Parameters:
        pulses  - (Optional) amount of pulses to add to counter
        """
        self.pulses += pulses
