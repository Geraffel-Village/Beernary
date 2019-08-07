import ConfigParser
import io

import B33rn4ryExceptions

class B33rn4ryDatabase():
  
  Database = None


  def __init__(self, dbtype='MYSQL'):
    if dbtype == 'MYSQL':
      self.Database = MysqlDatabase()
    elif dbtype == 'CONSOLE':
      self.Database = ConsoleDatabase()
    else:
      raise(NotImplementedError("unknown databse-type"))
    
  def checkUser(self, userID):
    return self.Database.checkUser(userID)
  
  def getUsers(self):
    return self.Database.getUsers()

  def storeDraft(self, userID, pulses):
    self.Database.storeDraft(userID, pulses)

  def getKegPulses(self, kegNum):
    return self.Database.getKegPulses(kegNum)
    
  def setKegPulses(self, kegNum, pulses):
    self.Database.setKegPulses(kegNum, pulses)
      
  def userConsumed(self):
    return -1

  def getEvents(self):
    return self.Database.getEvents()
  
  def addUser(self, ID, newUsername):
    return self.Database.addUser(ID, newUsername)

  def newKeg(self, event, volume):
    self.Database.newKeg(event, volume)
  
  def getCurrentKeg(self, eventid):
    return self.Database.getCurrentKeg(eventid)

  def getEventName(self, eventid):
    return self.Database.getEventName(eventid)
  
  def setEventActive(self, eventid):
    self.Database.setEventActive(eventid)
  
  def getActiveEvent(self):
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
  
  def __init__(self):
    import MySQLdb

    with open("config.ini") as f:
      b33rn4ry_config = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(b33rn4ry_config))

    dbhost = config.get('mysql', 'host')
    dbuser = config.get('mysql', 'user')
    dbpass = config.get('mysql', 'passwd')
    db= config.get('mysql', 'db')

    # Connect to mySQL db
    self.db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=db)
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

  def newKeg(self, event, volume):
    # mark current Keg as empty
    self.cursor.execute("UPDATE `keg` SET `isempty`=True WHERE eventid=%d AND isEmpty=False;" % (event))
    if self.cursor.rowcount <> 1:
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
  
