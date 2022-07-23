import serial
import syslog
import B33rn4ryExceptions
import binascii

class UsbRfid:
  # RFID start and end flags
  RFID_START = "\x04"
  RFID_END = "\x02"

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
    print ("read rfid")
    data = self.ser.read(1)
    while data != self.RFID_START and data != '':
      data = self.ser.read(1)
    data = self.ser.read(10)
    if data != '':
      return data

  def close(self):
    self.ser.close()

class SerialRfid:
  # RFID start and end flags
  RFID_START = 2
  RFID_END = 3

  SERIAL_DEVICE = ''
  BAUDRATE = 9600
  ser = None

  STATE_IDLE = 0
  STATE_START_RECEIVED = 1
  STATE_STOP_RECEIVED = 2
  STATE_READING_TAG = 3
  STATE_READING_CKSUM = 5
  state = None

  def __init__(self, device):
    self.SERIAL_DEVICE = device
    self.state = self.STATE_IDLE

  def initialize(self):
    try:
      self.ser = serial.Serial(self.SERIAL_DEVICE, self.BAUDRATE, timeout=1) 
    except serial.serialutil.SerialException:
      syslog.syslog(syslog.LOG_ERR, "Could not open serial device " + self.SERIAL_DEVICE);
    syslog.syslog("Serial-RFID reader initialized")

  def read_rfid(self):
    result = ''

    if self.ser is None:
      print("init reader")

    # read one byte with timeout
    for data in self.ser.read(1):

      if data == '':
        print ("read-timeout")
        self.state = self.STATE_IDLE
      elif data == self.RFID_START:
        print ("found START-byte")
        self.state = self.STATE_START_RECEIVED
      elif self.state == self.STATE_START_RECEIVED:
        print ("reading TAG data")
        try:
          result = self._read_tagdata_()
        except ValueError:
          print("invalid reading")
#        self.ser.reset_input_buffer()
          self.ser.flushInput()
          self.state = self.STATE_IDLE
        # read next byte, which sould be the STOP-Byte
#        data = self.ser.read(1)
#        self.ser.reset_input_buffer()
        self.ser.flushInput()
      elif data == self.RFID_END:
        print ("found STOP-byte")
#        self.ser.reset_input_buffer()
        self.ser.flushInput()
        self.state = self.STATE_IDLE
        break

#    print "data:" + binascii.hexlify(data)
#    while data == self.RFID_START and data != '':
#      print ("found START-byte or read-timeout")
#      data = self.ser.read(1)
#    data = self.ser.read(10)
#    if  != '':
    return result

  def _read_tagdata_(self):
    cksum_calc = 0x00
    result = ""
    tagdata = []
      # read next 10 bytes (remaining 9 of TAG + 1 byte cksum)
    data = self.ser.read(10)

    cksum_read_ascii = self.ser.read(1)
#    data="62e3086ced"
#    cksum_read_ascii = 0x08
    #print("debug: data:" + data + "; cksum:" + cksum_read_ascii)
#        print "debug: " + hex(int(data, 16))
#        print str(binascii.a2b_hex(data))
    for x in range(0,5):
      # copy 2 bytes of ascii-string (10 chars; 5 bytes)
      byte = data[x*2:x*2+2]
      print(byte)
      # store read data in tagdata[0..4] as interger
      tagdata.append(int(byte, 16))
#      print binascii.a2b_hex(hnibble+lnibble)
#         print hnibble 

    cksum_read = int(cksum_read_ascii, 16)
#    cksum_read = cksum_read_ascii

    for x in tagdata:
      cksum_calc = cksum_calc ^ x
      print("cksum: %x" % cksum_calc)
    #if cksum_calc != cksum_read:
      #print("cksum do not match")
    #else:
    result = data[1:9].decode('ASCII')
    print("Tag data:"+result)
    return str(result)

  def close(self):
    self.ser.close()
