#import
import serial
import syslog
import B33rn4ryExceptions

# RFID start and end flags
RFID_START = "\x04"
RFID_END = "\x02"

class UsbRfid:
  SERIAL_DEVICE = ''
  BAUDRATE = 9600
  ser = None

  def __init__(self, device):
    self.SERIAL_DEVICE = device

  def initialize(self):
    try:
      self.ser = serial.Serial(self.SERIAL_DEVICE, self.BAUDRATE, timeout=1) 
    except serial.serialutil.SerialException:
      syslog.syslog(syslog.LOG_ERR, "Could not open serial device " + self.SERIAL_DEVICE);
    syslog.syslog("USB-RFID reader initialized")

  def read_rfid(self):
    if self.ser is None:
      print("init reader")
    data = self.ser.read(1)
    while data != RFID_START and data != '':
      data = self.ser.read(1)
    data = self.ser.read(10)
    if data != '':
      return data

  def close(self):
    self.ser.close()

