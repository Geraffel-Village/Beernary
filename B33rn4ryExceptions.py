class B33rn4rySetupEventError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class B33rn4ryKegError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class DatabaseException(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class ReaderCommError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)
