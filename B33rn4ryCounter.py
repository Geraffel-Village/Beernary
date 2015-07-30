import sys
import os
sys.path.append('/home/florian/Desktop/b33rn4rycounter')
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QMessageBox, QDialog
from PyQt4.QtSql import *
import MySQLdb
import serial
import time
#from newUser import Ui_newUserDialog

# RFID start and end flags
RFID_START = "\x02"
RFID_END = "\x04"

# Serial bitrate for RFID reader
SERIAL_DEVICE = "/dev/ttyUSB0"
BAUDRATE = 9600

Ui_MainWindow, QtBaseClass = uic.loadUiType("B33rn4ryCounter.ui")
Ui_newUserDialog, QtBaseClass = uic.loadUiType("newUser.ui")

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.exitButton.clicked.connect(self.exitButtonClicked)
        self.newUserButton.clicked.connect(self.newUser)
        self.actionQuit.triggered.connect(self.exitButtonClicked)
        self.actionNewUser.triggered.connect(self.newUser)
        self.delUserButton.clicked.connect(self.deleteUser)
        global db
        try:
            db = MySQLdb.connect("192.168.2.115","b33rn4ry","b33rn4ry","b33rn4rycounter" )
        except:
            self.statusBar().showMessage('Error connecting database!')
        else:
            self.statusBar().showMessage('Database connection established!')
        global headernames
        headernames = ["IDhex", "ID", "Name", "Timestamp"]
        self.userTable.setHorizontalHeaderLabels(headernames)
        if (db):
            global cursor
            cursor = db.cursor()
            self.refreshUserTable()
        self.refreshButton.clicked.connect(self.refreshUserTable)

    def exitButtonClicked(self):
        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle("Quit?");
        msgBox.setText("Are you sure you want to quit?")
        msgBox.setStandardButtons(QMessageBox.No|QMessageBox.Yes)
        msgBox.setDefaultButton(QMessageBox.Yes)
        msgBox.exec_
        if msgBox.exec_() == QMessageBox.Yes:
            QtGui.qApp.quit()

    def refreshUserTable(self):
        self.userTable.setRowCount(0)
        self.userTable.setHorizontalHeaderLabels(headernames)
        cursor.execute("SELECT `id`, `name`, `timestamp` FROM users WHERE 1 ORDER BY `timestamp` DESC;")
        db.commit()
        rows = cursor.fetchall() 
        for row in rows:
            self.userTable.insertRow(self.userTable.rowCount()) 
            itm1 = QtGui.QTableWidgetItem(str(row[0]), 0) 
            self.userTable.setItem(self.userTable.rowCount()-1, 0, itm1) 
            pID = str(int(row[0][2:], 16))
            itm2 = QtGui.QTableWidgetItem(str(pID.zfill(10)), 0) 
            self.userTable.setItem(self.userTable.rowCount()-1, 1, itm2) 
            itm3 = QtGui.QTableWidgetItem(str(row[1]), 0) 
            self.userTable.setItem(self.userTable.rowCount()-1, 2, itm3) 
            itm4 = QtGui.QTableWidgetItem(str(row[2]), 0) 
            self.userTable.setItem(self.userTable.rowCount()-1, 3, itm4) 
            self.userTable.update()
        self.userTable.hideColumn(0)

    def deleteUser(self):
        self.userTable.showColumn(0)
        index = self.userTable.selectedIndexes()
        if index:
            userId = self.userTable.model().data(index[0]).toString()
            try:
                sql = "DELETE FROM `users` WHERE `id` = '%s';" % userId
                cursor.execute(sql)
                db.commit()
            except:
                print("Error executing SQL statement!")
            self.userTable.hideColumn(0)
            self.refreshUserTable()

    def newUser(self):
        form = QtGui.QDialog()
        newUserWindow.show()

class newUserDialog(QtGui.QDialog, Ui_newUserDialog):
    def __init__(self, parent=MainWindow):
        QtGui.QDialog.__init__(self)
        Ui_newUserDialog.__init__(self)
        self.setupUi(self)
        self.readRfidButton.clicked.connect(self.readRFID)
        self.buttonBox.accepted.connect(self.addUser)
        self.buttonBox.rejected.connect(self.clearFields)

    def addUser(self):
        palette = QtGui.QPalette()
        username = self.lineUserName.text()
        cursor.execute("SELECT COUNT(*) FROM `users` WHERE `id` = '%s';" % ID)
        result = cursor.fetchone()
        if result[0] > 0:
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            window.labelMessage.setText("Error: User ID exists!")
        else:
            cursor.execute("INSERT IGNORE INTO `users` SET `id`='%s', `name` = '%s';" % (ID, username))
            db.commit()
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)
            window.labelMessage.setText("User added succesfully!")
        window.refreshUserTable()
        window.labelMessage.setPalette(palette)

    def readRFID(self):
        global ID
        ID = ""
        ID = read_rfid()
        if ID:
            pID = str(int(ID[2:], 16))
            self.lineRFIDno.setText("%s" % pID.zfill(10))
        else:
            self.lineRFIDno.setText("Error!")

    def clearFields(self):
        self.lineRFIDno.setText("")
        self.lineUserName.setText("")

def read_rfid():
    try:
        ser = serial.Serial(SERIAL_DEVICE, BAUDRATE, timeout=1)
    except serial.serialutil.SerialException:
        print "Could not open serial device " +SERIAL_DEVICE
    data = ser.read(1)
    i = 1
    while data != 'R' and i < 10 and data != '':
        i += 1
        data = ser.read(1)
    if i < 5:
        data = ser.read(10)
        ser.close()
        return data
    else:
        return 0

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    newUserWindow = newUserDialog()
    sys.exit(app.exec_())
