import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QMessageBox
from PyQt4.QtSql import *
import MySQLdb

Ui_MainWindow, QtBaseClass = uic.loadUiType("B33rn4ryCounter.ui")

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.exitButton.clicked.connect(self.exitButtonClicked)
        self.actionQuit.triggered.connect(self.exitButtonClicked)
        self.delUserButton.clicked.connect(self.deleteUser)
        global db
        try:
            db = MySQLdb.connect("192.168.2.115","b33rn4ry","b33rn4ry","b33rn4rycounter" )
        except:
            self.statusBar().showMessage('Error connecting database!')
        else:
            self.statusBar().showMessage('Database connection established!')
        global headernames
        headernames = ["ID", "Name", "Timestamp"]
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
        rows = cursor.fetchall() 
        for row in rows:
            self.userTable.insertRow(self.userTable.rowCount()) 
            itm1 = QtGui.QTableWidgetItem(str(row[0]), 0) 
            self.userTable.setItem(self.userTable.rowCount()-1, 0, itm1) 
            itm2 = QtGui.QTableWidgetItem(str(row[1]), 0) 
            self.userTable.setItem(self.userTable.rowCount()-1, 1, itm2) 
            itm3 = QtGui.QTableWidgetItem(str(row[2]), 0) 
            self.userTable.setItem(self.userTable.rowCount()-1, 2, itm3) 
            self.userTable.update()

    def deleteUser(self):
        index = self.userTable.selectedIndexes()
        if index:
            userId = self.userTable.model().data(index[0]).toString()
            try:
                sql = "DELETE FROM `users` WHERE `id` = '%s';" % userId
                cursor.execute(sql)
                db.commit()
            except:
                print("Error executing SQL statement!")
            self.refreshUserTable()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
