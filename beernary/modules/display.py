#!/usr/bin/python3

"""
Controls the beenary's integrated display. Supports different types (abstract base class).
"""

from abc import ABC, abstractmethod
import time
import threading

try:
    import RPi.GPIO as GPIO
except:  # pylint: disable=bare-except
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
    """Represents a the currently installed LCD display (probably HD44780)."""

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

        self._enabled = False
        self._lock = threading.Lock()

        # robuste 4-Bit-Initialisierung
        self._power_up_init()

    def _power_up_init(self):
        """Robust init sequence for HD44780 in 4-bit mode."""
        time.sleep(0.05)  # >= 40 ms nach Power-Up

        # 3x 0x30 im 8-bit Fake-Mode (nur High-Nibble senden)
        for _ in range(3):
            self._write_nibble(0x30, rs=False)
            time.sleep(0.0045)  # >= 4.1 ms

        # Wechsel in 4-bit Mode: 0x20 (nur High-Nibble)
        self._write_nibble(0x20, rs=False)
        time.sleep(0.0001)

        # Jetzt normale Befehle als volle Bytes
        self._cmd(0x28)  # Function Set: 4bit, 2 lines, 5x8 dots
        self._cmd(0x0C)  # Display ON, Cursor OFF, Blink OFF
        self.clear()
        self._cmd(0x06)  # Entry Mode

    @property
    def enabled(self):
        """Returns status of display backlight (on/off)"""
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        """Sets status of display backlight (on/off)"""
        self._enabled = bool(value)
        GPIO.output(self.LCD_LIGHT, self._enabled)

    def toggle_clock_enable(self):
        """Toggles the clock enable pin of the LCD display to execute instructions."""
        time.sleep(self.E_DELAY)
        GPIO.output(self.LCD_E, True)
        time.sleep(self.E_PULSE)
        GPIO.output(self.LCD_E, False)
        time.sleep(self.E_DELAY)

    def _write_nibble(self, nibble, rs: bool):
        GPIO.output(self.LCD_RS, rs)

        GPIO.output(self.LCD_D4, bool(nibble & 0x10))
        GPIO.output(self.LCD_D5, bool(nibble & 0x20))
        GPIO.output(self.LCD_D6, bool(nibble & 0x40))
        GPIO.output(self.LCD_D7, bool(nibble & 0x80))

        self.toggle_clock_enable()

    def _cmd(self, cmd: int):
        self.send_bit(cmd, self.LCD_CMD)

        # Extra Delay für langsame Befehle
        if cmd in (0x01, 0x02):  # CLEAR / HOME
            time.sleep(0.0022)   # >= 2 ms

    def send_bit(self, bits, mode):
        GPIO.output(self.LCD_RS, mode)

        # High bits
        GPIO.output(self.LCD_D4, bool(bits & 0x10))
        GPIO.output(self.LCD_D5, bool(bits & 0x20))
        GPIO.output(self.LCD_D6, bool(bits & 0x40))
        GPIO.output(self.LCD_D7, bool(bits & 0x80))
        self.toggle_clock_enable()

        # Low bits
        GPIO.output(self.LCD_D4, bool(bits & 0x01))
        GPIO.output(self.LCD_D5, bool(bits & 0x02))
        GPIO.output(self.LCD_D6, bool(bits & 0x04))
        GPIO.output(self.LCD_D7, bool(bits & 0x08))
        self.toggle_clock_enable()

    def send_message(self, message, line, style):
        with self._lock:
            try:
                # Style
                if style == "centred":
                    message = message.center(self.LCD_WIDTH," ")
                elif style == "ljust":
                    message = message.ljust(self.LCD_WIDTH," ")
                elif style == "rjust":
                    message = message.rjust(self.LCD_WIDTH," ")
                else:
                    raise AttributeError(f"Unknown message style: {style}")

                # Arschtritt vor Ausgabe
                self._cmd(0x28)  # Function Set
                self._cmd(0x0C)  # Display ON

                # Zeilenadresse
                if   line == 1: self._cmd(self.LCD_LINE_1)
                elif line == 2: self._cmd(self.LCD_LINE_2)
                elif line == 3: self._cmd(self.LCD_LINE_3)
                elif line == 4: self._cmd(self.LCD_LINE_4)
                else:
                    raise AttributeError(f"Unknown display line: {line}")

                # Zeichen ausgeben
                for i in range(self.LCD_WIDTH):
                    self.send_bit(ord(message[i]), self.LCD_CHR)

                if self.LCD_STDOUT:
                    print(message)

            except Exception:
                # Fallback: Re-Init und Wiederholung
                self.reinit()

                self._cmd(0x28)
                self._cmd(0x0C)

                if   line == 1: self._cmd(self.LCD_LINE_1)
                elif line == 2: self._cmd(self.LCD_LINE_2)
                elif line == 3: self._cmd(self.LCD_LINE_3)
                elif line == 4: self._cmd(self.LCD_LINE_4)

                for i in range(self.LCD_WIDTH):
                    self.send_bit(ord(message[i]), self.LCD_CHR)

    def clear(self):
        with self._lock:
            self._cmd(0x01)  # CLEAR

    def reinit(self):
        with self._lock:
            self._power_up_init()

    def close(self):
        GPIO.cleanup()
