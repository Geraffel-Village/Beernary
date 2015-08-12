class B33rn4ryDatabase():
  
  Database = None

  def __init__(self, dbtype='MYSQL'):
    if dbtype == 'MYSQL':
      self.Database = MysqlDatabase()
    elif dbtype == 'FILE':
      self.Database = FileDatabase()
    else:
      raise(NotImplementedError("unknown databse-type"))
    
  def checkUser(self, userID):
    return self.Database.checkUser(userID)
      
  def userConsumed(self):
    return -1

class FileDatabase():

  def checkUser(self, userID):
    if userID == 'valid':
      return ['geraffel-user',]
    
  def userConsumed(self, userID):
    return -1

class MysqlDatabase():

  db = None
  cursor = None
  
  def __init__(self):
    import MySQLdb

    # Connect to mySQL db
    self.db = MySQLdb.connect(host="localhost", user="b33rn4ry", passwd="b33rn4ry", db="b33rn4rycounter")
    self.cursor=db.cursor()

  def checkUser(self, userID):
    self.cursor.execute ("SELECT `name` FROM `users` WHERE id = '"+userID+"';")
    return self.cursor.fetchone()

