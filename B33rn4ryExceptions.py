class B33rn4rySetupEventError(Exception):
  """
  This Exception will be raised when there is something wrong / unacceptable in the setup of the
  Event-Configuration, e.g. no active event.
  """
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class B33rn4ryKegError(Exception):
  """
  This Exception will be raised when there is something wrong with the setup of the keg,
  e.g. no empty kegs defined.
  """
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

