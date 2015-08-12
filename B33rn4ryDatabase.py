claas Beern4ryDatabase(dbtype = MYSQL):
  
  def __init__(self, dbtype):
    if dbtype == 'MYSQL':
      Database = MysqlDatabase()
    elif dbtype == 'FILE':
      Database = FileDatabase()
    else:
      raise(NotImplementedError("unknown databse-type"))
    
  def checkUser(self, userID):
    if dbtype == 'MYSQL':
      
  def userConsumed(self):

class FileDatabase():
  def checkUser(self, userID):
    if userID == 'valid':
      return ['geraffel-user',]
    
  def userConsumed(self, userID):

class MysqlDatabase();
  import MySQLdb

  db = None
  cursor = None
  
  def __init__(self):
    # Connect to mySQL db
    self.db = MySQLdb.connect(host="localhost", user="b33rn4ry", passwd="b33rn4ry", db="b33rn4rycounter")
    self.cursor=db.cursor()

  def checkUser(self, userID):
    self.cursor.execute ("SELECT `name` FROM `users` WHERE id = '"+userID+"';")
    return self.cursor.fetchone()
