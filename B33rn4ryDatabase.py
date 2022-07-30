import B33rn4ryExceptions

class B33rn4ryDatabase():
  """
  This class is the interface to to have access the underlaying database.
  It currently supports only "MYSQL" (for production), but there is also a
  basic-type "CONSOLE" (for debugging / development). This class provides 
  enough abstraction, that the counter and the registry can manage all 
  relevant tasks by it.
  """

  Database = None


  def __init__(self, dbtype='MYSQL', **kwargs):
    """
    Initializes the basic database-connection, by default the "MYSQL"-type is used.
    The reference to the current database is kept in the private variable "Database".
    """
    if dbtype == 'MYSQL':
      self.Database = MysqlDatabase(**kwargs)
    elif dbtype == 'CONSOLE':
      self.Database = ConsoleDatabase()
    else:
      raise(NotImplementedError("unknown databse-type"))
    
  def checkUser(self, userID):
    return self.Database.checkUser(userID)
  
  def getUsers(self):
    """
    Abstract method to return a list of all users from the database.
    """
    return self.Database.getUsers()

  def storeDraft(self, userID, pulses):
    self.Database.storeDraft(userID, pulses)

  def getKegPulses(self, kegNum):
    """
    Abstract method to return the sum of counts for the provided keg.
    """
    return self.Database.getKegPulses(kegNum)
    
  def setKegPulses(self, kegNum, pulses):
    """
    Abstract method to set the absolute number of counts for a keg.
    """
    self.Database.setKegPulses(kegNum, pulses)
      
  def userConsumed(self):
    return -1

  def getEvents(self):
    """
    Abstract method to return a list of all events defined in the database.
    """
    return self.Database.getEvents()
  
  def addUser(self, ID, newUsername):
    """
    Abstract method to setup a new user with "newUsername" and transponderid "ID" 
    in the database.
    """
    return self.Database.addUser(ID, newUsername)

  def deleteUser(self, ID):
    return self.Database.deleteUser(ID)

  def newKeg(self, event, volume):
    """
    Abstract method to define a new full keg in th database and assign it to event "event".
    "Volume" is a literal string, defining the nominal amount of content, e.g. "50l", "20l".
    """
    self.Database.newKeg(event, volume)
  
  def getCurrentKeg(self, eventid):
    """
    Abstract method to return the currently active keg of the event "eventid".
    """
    return self.Database.getCurrentKeg(eventid)

  def getEventName(self, eventid):
    """
    Abstract method to return the name of the event "eventid".
    """
    return self.Database.getEventName(eventid)
  
  def setEventActive(self, eventid):
    """
    Abstract method to set the event "eventid" as the only active event in the list of all
    defined events.
    """
    self.Database.setEventActive(eventid)
  
  def getActiveEvent(self):
    """
    Abstract method to return the eventid of the currently active event.
    """
    return self.Database.getActiveEvent()
  
class ConsoleDatabase():

  validUsers = {
    '001',
    '3800C9C3B7',
#    '3800CA2422',
  }
  
  def checkUser(self, userID):
    if userID in self.validUsers:
      return ['user'+userID,]
    
  def userConsumed(self, userID):
    return -1
  
  def storeDraft(self, userID, pulses):
    print "user drafted %d pulses" % pulses

class MysqlDatabase():

  db = None
  cursor = None
  
  def __init__(self, **kwargs):
    import MySQLdb

    # Connect to mySQL db
    self.db = MySQLdb.connect(**kwargs)
    self.cursor=self.db.cursor()
    
  def checkUser(self, userID):
    self.cursor.execute ("SELECT `name` FROM `users` WHERE id = '"+userID+"';")
    return self.cursor.fetchone()

  def getUsers(self):
    self.cursor.execute ("SELECT `id`, `name`, `timestamp` FROM users ORDER BY `timestamp` DESC;")
    return self.cursor.fetchall()

  def storeDraft(self, userID, pulses):
    self.cursor.execute ("Insert INTO `consume` (id, pulses) VALUES ('%s', %d)" % (userID, pulses) )  
    self.db.commit()
    print "user drafted %d pulses" % pulses

  def getKegPulses(self, kegNum):
    self.cursor.execute ("SELECT pulses FROM `keg` WHERE kegid=%d" % kegNum)
    return self.cursor.fetchone()[0]
    
  def setKegPulses(self, kegNum, pulses):
    self.cursor.execute ("UPDATE `keg` SET pulses=%d WHERE kegid=%d" % (pulses, kegNum) )
    self.db.commit()
  
  def getEvents(self):
    self.cursor.execute ("SELECT name, eventid FROM `event` ORDER by name")
    return self.cursor.fetchall()
  
  def addUser(self, ID, newUsername):
    self.cursor.execute("SELECT id FROM `users` WHERE `id` = '%s';" % ID)
    if self.cursor.rowcount != 0:
      raise NotImplementedError("Id already registered")
    self.cursor.execute("SELECT name FROM `users` WHERE `name` = '%s';" % newUsername)
    if self.cursor.rowcount != 0:
      raise NotImplementedError("adding dublicate Username not implemented")
    self.cursor.execute("INSERT IGNORE INTO `users` SET `id`='%s', `name` = '%s';" % (ID, newUsername))
    self.db.commit()

  def deleteUser(self, ID):
    try:
      self.cursor.execute("DELETE from `users` where `id` = '%s';" % ID)
      self.db.commit()
    except MySQLdb.Error, e:
      raise DatabaseException("DatabaseError: ", e)

  def newKeg(self, event, volume):
    # mark current Keg as empty
    self.cursor.execute("UPDATE `keg` SET `isempty`=True WHERE eventid=%d AND isEmpty=False;" % (event))
    if self.cursor.rowcount == 0:
      print "first keg for event added"
    elif self.cursor.rowcount <> 1:
      self.db.rollback()
      raise RuntimeError("wrong # of kegs for this event")
    self.cursor.execute ("Insert INTO `keg` (eventid, volume) VALUES (%d, %d)" % (event, volume) )
    self.db.commit()
  
  def getCurrentKeg(self, eventid):
    self.cursor.execute("SELECT kegid FROM `keg` WHERE eventid = %d AND isEmpty=False;" % eventid)
    if self.cursor.rowcount != 1:
      raise B33rn4ryExceptions.B33rn4ryKegError("invalid # of Kegs active")
    assert self.cursor.rowcount == 1
    return self.cursor.fetchone()[0]

  def getEventName(self, eventid):
    self.cursor.execute ("SELECT `name` FROM `event` WHERE eventid=%d;" % eventid )
    return self.cursor.fetchone()[0]
    
  def setEventActive(self, eventid):
    self.cursor.execute("SELECT `eventid` FROM `event` where selected=true;")
    if self.cursor.rowcount == 1:
      if self.cursor.fetchone()[0] == eventid:
#        print "all setup"
        pass
      else:
#        print "deselect all trues"
        self.cursor.execute("UPDATE `event` SET `selected`=False WHERE selected=True;")
    else:
#      print "set all false, setting only event"
      self.cursor.execute("UPDATE `event` SET `selected`=False WHERE eventid <> %d;" % eventid)
#    print "setting only event"
    self.cursor.execute("UPDATE `event` SET `selected`=True WHERE eventid = %d;" % eventid)
    self.db.commit()

  def getActiveEvent(self):
    self.cursor.execute("SELECT eventid, name FROM `event` where selected=true;")
    if self.cursor.rowcount != 1:
      raise B33rn4ryExceptions.B33rn4rySetupEventError("faulty configuration in Event-setup")
    
    assert self.cursor.rowcount == 1
    return self.cursor.fetchone()
  
