#!/usr/bin/python3

"""
Controls the beenary's integrated display. Supports different types (abstract base class).
"""

from abc import ABC, abstractmethod
import time

try:
    import RPi.GPIO as GPIO
except: # pylint: disable=bare-except
    import Mock.GPIO as GPIO


class Display(ABC):
    """Abstract base class to describe functionality of the beernary's inbuilt display."""

    @property
    @abstractmethod
    def enabled(self):
        """
        Abstract property to reflect state of the display (enabled/disabled).
        External API implemented via property.getter and property.setter
        """

    @abstractmethod
    def __init__(self):
        """Abstract constructor to initialize the display (e.g. set cursor mode)."""

    @abstractmethod
    def send_message(self, message: str, line: int, style: str):
        """
        Abstract method to send a message to the display.

        Parameters:
        message - message to display
        line    - line of the display for message
        style   - style of the message:
            "centred"  - Centred          (ex. 2)
            "ljust"    - Left justified   (ex. 1)
            "rjust"    - Right justified  (ex. 3)
        """

    @abstractmethod
    def close(self):
        """Abstract method to close the object, e.g. clean GPIO pins."""

class LCDDisplay(Display):
    """Represents a the currently installed LCD display (propably HD44780)."""

    # Constants
    LCD_RS      = 25
    LCD_E       = 24
    LCD_D4      = 23
    LCD_D5      = 17
    LCD_D6      = 27
    LCD_D7      = 22
    LCD_LIGHT   =  4
    LCD_WIDTH   = 20        # Maximum characters per line
    LCD_CHR     = True
    LCD_CMD     = False
    LCD_LINE_1  = 0x80      # LCD RAM address for the 1st line
    LCD_LINE_2  = 0xC0      # LCD RAM address for the 2nd line
    LCD_LINE_3  = 0x94      # LCD RAM address for the 3rd line
    LCD_LINE_4  = 0xD4      # LCD RAM address for the 4th line
    E_PULSE     = 0.0005
    E_DELAY     = 0.0005
    LCD_STDOUT  = False

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.LCD_RS, GPIO.OUT) # RS
        GPIO.setup(self.LCD_E, GPIO.OUT)  # E
        GPIO.setup(self.LCD_D4, GPIO.OUT) # DB4
        GPIO.setup(self.LCD_D5, GPIO.OUT) # DB5
        GPIO.setup(self.LCD_D6, GPIO.OUT) # DB6
        GPIO.setup(self.LCD_D7, GPIO.OUT) # DB7
        GPIO.setup(self.LCD_LIGHT, GPIO.OUT) # Backlight

        self.send_bit(0x33, self.LCD_CMD) # 110011 Initialize
        self.send_bit(0x32, self.LCD_CMD) # 110010 Initialize
        self.send_bit(0x06, self.LCD_CMD) # 000110 Cursor move direction
        self.send_bit(0x0C, self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        self.send_bit(0x28, self.LCD_CMD) # 101000 Data length, number of lines, font size
        self.send_bit(0x01, self.LCD_CMD) # 000001 Clear display

        time.sleep(self.E_DELAY)

        self.enabled = False

    @property
    def enabled(self):
        """Returns status of display backlight (on/off)"""
        return self.enabled

    @enabled.setter
    def enabled(self, value):
        """Sets status of display backlight (on/off)"""
        GPIO.output(self.LCD_LIGHT, value)

    def toggle_clock_enable(self):
        """Toggles the clock enable pin of the LCD display to execute instructions."""

        time.sleep(self.E_DELAY)
        GPIO.output(self.LCD_E, True)
        time.sleep(self.E_PULSE)
        GPIO.output(self.LCD_E, False)
        time.sleep(self.E_DELAY)

    def send_bit(self, bits, mode):
        """
        Sends input bits (characters or commands) to the LCD display.

        Parameters:
        bits - data to send (character or command)
        mode - data mode
          true   - Character
          false  - Command
        """
        GPIO.output(self.LCD_RS, mode)

        # High bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)

        if bits&0x10 == 0x10:
            GPIO.output(self.LCD_D4, True)
        if bits&0x20 == 0x20:
            GPIO.output(self.LCD_D5, True)
        if bits&0x40 == 0x40:
            GPIO.output(self.LCD_D6, True)
        if bits&0x80 == 0x80:
            GPIO.output(self.LCD_D7, True)

        self.toggle_clock_enable()

        # Low bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)

        if bits&0x01==0x01:
            GPIO.output(self.LCD_D4, True)
        if bits&0x02==0x02:
            GPIO.output(self.LCD_D5, True)
        if bits&0x04==0x04:
            GPIO.output(self.LCD_D6, True)
        if bits&0x08==0x08:
            GPIO.output(self.LCD_D7, True)

        self.toggle_clock_enable()

    def send_message(self, message, line, style):

        # Handle style for message
        if style == "centred":
            message = message.center(self.LCD_WIDTH," ")
        elif style == "ljust":
            message = message.ljust(self.LCD_WIDTH," ")
        elif style == "rjust":
            message = message.rjust(self.LCD_WIDTH," ")
        else:
            raise AttributeError(f"Unknown message style: {style}")

        # Handle line for message
        if line   == 1:
            self.send_bit(self.LCD_LINE_1, self.LCD_CMD)
        elif line == 2:
            self.send_bit(self.LCD_LINE_2, self.LCD_CMD)
        elif line == 3:
            self.send_bit(self.LCD_LINE_3, self.LCD_CMD)
        elif line == 4:
            self.send_bit(self.LCD_LINE_4, self.LCD_CMD)
        else:
            raise AttributeError(f"Unknown display line: {line}")

        # split message longer than LCD_WITH
        for i in range(self.LCD_WIDTH):
            self.send_bit(ord(message[i]),self.LCD_CHR)

        # send message to STDOUT too, if configured
        if self.LCD_STDOUT is True:
            print(message)

    def clear(self):
        """Clears the display."""
        self.send_bit(0x01, self.LCD_CMD)

    def close(self):
        GPIO.cleanup()
