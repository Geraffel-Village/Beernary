# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newUser.ui'
#
# Created: Wed Jul 29 23:54:25 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_newUserDialog(object):
    def setupUi(self, newUserDialog):
        newUserDialog.setObjectName(_fromUtf8("newUserDialog"))
        newUserDialog.resize(400, 184)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        newUserDialog.setWindowIcon(icon)
        self.newUserBox = QtGui.QDialogButtonBox(newUserDialog)
        self.newUserBox.setGeometry(QtCore.QRect(30, 140, 341, 32))
        self.newUserBox.setOrientation(QtCore.Qt.Horizontal)
        self.newUserBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.newUserBox.setObjectName(_fromUtf8("newUserBox"))
        self.label = QtGui.QLabel(newUserDialog)
        self.label.setGeometry(QtCore.QRect(31, 77, 75, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.lineUserName = QtGui.QLineEdit(newUserDialog)
        self.lineUserName.setGeometry(QtCore.QRect(112, 71, 129, 27))
        self.lineUserName.setObjectName(_fromUtf8("lineUserName"))
        self.lineRFIDno = QtGui.QLineEdit(newUserDialog)
        self.lineRFIDno.setGeometry(QtCore.QRect(110, 30, 129, 27))
        self.lineRFIDno.setObjectName(_fromUtf8("lineRFIDno"))
        self.label_2 = QtGui.QLabel(newUserDialog)
        self.label_2.setGeometry(QtCore.QRect(31, 34, 43, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(newUserDialog)
        QtCore.QObject.connect(self.newUserBox, QtCore.SIGNAL(_fromUtf8("accepted()")), newUserDialog.accept)
        QtCore.QObject.connect(self.newUserBox, QtCore.SIGNAL(_fromUtf8("rejected()")), newUserDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(newUserDialog)

    def retranslateUi(self, newUserDialog):
        newUserDialog.setWindowTitle(_translate("newUserDialog", "New User", None))
        self.label.setText(_translate("newUserDialog", "User name:", None))
        self.label_2.setText(_translate("newUserDialog", "RFID#", None))

