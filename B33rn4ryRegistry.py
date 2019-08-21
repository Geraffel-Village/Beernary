#!/usr/bin/python

import sys, io, os
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QMessageBox, QDialog
from PyQt4.QtSql import *
import B33rn4ryDatabase
import serial
import ConfigParser

# RFID start and end flags
RFID_START = "\x04"
RFID_END = "\x02"

BAUDRATE = 9600

Ui_MainWindow, QtBaseClass = uic.loadUiType("B33rn4ryRegistry.ui")
Ui_newUserDialog, QtBaseClass = uic.loadUiType("newUser.ui")
Ui_serviceDialog, QtBaseClass = uic.loadUiType("service.ui")

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    
    db = None
    currentEvent = None
    
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.exitButton.clicked.connect(self.exitButtonClicked)
        self.newUserButton.clicked.connect(self.newUser)
        self.actionQuit.triggered.connect(self.exitButtonClicked)
        self.actionNewUser.triggered.connect(self.newUser)
        self.delUserButton.clicked.connect(self.deleteUser)
        self.serviceButton.clicked.connect(self.serviceButtonClicked)
        if self.db:
          self.statusBar().showMessage('Error connecting database!')
        else:
          self.statusBar().showMessage('Database connection established!')
        global headernames
        headernames = ["IDhex", "ID", "Name", "Timestamp"]
        self.userTable.setHorizontalHeaderLabels(headernames)
        if (self.db):
            self.refreshUserTable()
        self.refreshButton.clicked.connect(self.refreshUserTable)

    def connectDB(self, dbhost, dbuser, dbpass, dbname):
        self.db = B33rn4ryDatabase.B33rn4ryDatabase(dbtype='MYSQL', host=dbhost, user=dbuser, passwd=dbpass, db=dbname)

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
        rows = self.db.getUsers()
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
        newUserWindow.clearFields()
        newUserWindow.show()
        newUserWindow.readRFID()

    def serviceButtonClicked(self):
        form = QtGui.QDialog()
        serviceWindow.show()

class newUserDialog(QtGui.QDialog, Ui_newUserDialog):
    
    ReaderDevice = None

    def __init__(self, ReaderDevice, parent=MainWindow):
        QtGui.QDialog.__init__(self)
        Ui_newUserDialog.__init__(self)
        self.setupUi(self)
        self.lineUserName.setFocus()
        self.readRfidButton.clicked.connect(self.readRFID)
        self.buttonBox.accepted.connect(self.addUser)
        self.buttonBox.rejected.connect(self.clearFields)
        self.ReaderDevice = ReaderDevice

    def addUser(self):
        palette = QtGui.QPalette()
        username = self.lineUserName.text()
        if username == '' or self.lineRFIDno == '':
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            window.labelMessage.setText("Error: User name or RFID# empty!")
        else:
            window.db.addUser(ID, username)
#                palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
#                window.labelMessage.setText("Error: User ID exists!")
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)
            window.labelMessage.setText("User added succesfully!")
            window.refreshUserTable()
        window.labelMessage.setPalette(palette)
        self.clearFields()

    def readRFID(self):
        global ID
        ID = ''
        ID = read_rfid(self.ReaderDevice)
        if ID:
            pID = str(int(ID[2:], 16))
            self.lineRFIDno.setText("%s" % pID.zfill(10))
        else:
            self.lineRFIDno.setText("Error!")

    def clearFields(self):
        self.lineRFIDno.setText("")
        self.lineUserName.setText("")

class serviceDialog(QtGui.QDialog, Ui_serviceDialog):

    def __init__(self, parent=MainWindow):
        QtGui.QDialog.__init__(self)
        Ui_serviceDialog.__init__(self)
        self.setupUi(self)
        self.newKegButton.clicked.connect(self.addKeg)
        self.acceptEventButton.clicked.connect(self.acceptEventButtonClicked)
        rows = window.db.getEvents()
        for row in rows:
            self.eventBox.addItem(row[0], row[1])
            listItem = QtGui.QListWidgetItem(row[0])
            listItem.setData(QtCore.Qt.UserRole, row[1])
            self.eventList.addItem(listItem)
        self.kegvolumeBox.addItem("50 L")
        self.kegvolumeBox.addItem("30 L")
        self.kegvolumeBox.addItem("20 L")
        self.kegvolumeBox.addItem("15 L")
        self.kegvolumeBox.addItem("10 L")
    
    def addKeg(self):
        eventid = self.eventBox.itemData(self.eventBox.currentIndex())
        kegvolume = str(self.kegvolumeBox.currentText()).strip(' L')
        window.db.newKeg(int(eventid.toInt()[0]), int(kegvolume) )
        window.statusBar().showMessage("new keg added for this event")
    
    def acceptEventButtonClicked(self):
        window.currentEvent = self.eventList.currentItem().data(QtCore.Qt.UserRole).toInt()[0]
        window.db.setEventActive(window.currentEvent)
        window.statusBar().showMessage(window.db.getEventName(window.currentEvent) + ' event gewaehlt')

def read_rfid(serialdevice):
    try:
        ser = serial.Serial(serialdevice, BAUDRATE, timeout=1)
    except serial.serialutil.SerialException:
        print "Could not open serial device " +serialdevice
    data = ser.read(1)
    while data != RFID_START and data != '':
        data = ser.read(1)
    data = ser.read(10)
    ser.close()
    if data != '':
        return data
    else:
        return 0

if __name__ == "__main__":
    with open("config.ini") as f:
        b33rn4ry_config = f.read()
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.readfp(io.BytesIO(b33rn4ry_config))
    
        dbhost = config.get('mysql', 'host')
        dbuser = config.get('mysql', 'user')
        dbpass = config.get('mysql', 'passwd')
        dbname = config.get('mysql', 'db')
        # Serial bitrate for RFID reader
        serialdevice = config.get('registry', 'comdevice')
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.connectDB(dbhost, dbuser, dbpass, dbname)
    window.refreshUserTable()
    newUserWindow = newUserDialog(serialdevice)
    serviceWindow = serviceDialog()
    sys.exit(app.exec_())
