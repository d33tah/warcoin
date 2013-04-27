# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/mainwindow.ui'
#
# Created: Sat Apr 27 16:19:38 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(699, 424)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.layoutGry = QtGui.QVBoxLayout()
        self.layoutGry.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.layoutGry.setObjectName(_fromUtf8("layoutGry"))
        self.widget = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.layoutGry.addWidget(self.widget)
        self.nrTuryLbl = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nrTuryLbl.sizePolicy().hasHeightForWidth())
        self.nrTuryLbl.setSizePolicy(sizePolicy)
        self.nrTuryLbl.setObjectName(_fromUtf8("nrTuryLbl"))
        self.layoutGry.addWidget(self.nrTuryLbl)
        self.nowaTuraBtn = QtGui.QPushButton(self.centralwidget)
        self.nowaTuraBtn.setObjectName(_fromUtf8("nowaTuraBtn"))
        self.layoutGry.addWidget(self.nowaTuraBtn)
        self.horizontalLayout.addLayout(self.layoutGry)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.nawiazanePolaczeniaLbl = QtGui.QLabel(self.centralwidget)
        self.nawiazanePolaczeniaLbl.setObjectName(_fromUtf8("nawiazanePolaczeniaLbl"))
        self.verticalLayout.addWidget(self.nawiazanePolaczeniaLbl)
        self.peerList = QtGui.QListView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.peerList.sizePolicy().hasHeightForWidth())
        self.peerList.setSizePolicy(sizePolicy)
        self.peerList.setObjectName(_fromUtf8("peerList"))
        self.verticalLayout.addWidget(self.peerList)
        self.rozlaczBtn = QtGui.QPushButton(self.centralwidget)
        self.rozlaczBtn.setEnabled(False)
        self.rozlaczBtn.setObjectName(_fromUtf8("rozlaczBtn"))
        self.verticalLayout.addWidget(self.rozlaczBtn)
        self.adresIpLayout = QtGui.QHBoxLayout()
        self.adresIpLayout.setObjectName(_fromUtf8("adresIpLayout"))
        self.adresIpLbl = QtGui.QLabel(self.centralwidget)
        self.adresIpLbl.setEnabled(False)
        self.adresIpLbl.setObjectName(_fromUtf8("adresIpLbl"))
        self.adresIpLayout.addWidget(self.adresIpLbl)
        self.adresIpEdit = QtGui.QLineEdit(self.centralwidget)
        self.adresIpEdit.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.adresIpEdit.sizePolicy().hasHeightForWidth())
        self.adresIpEdit.setSizePolicy(sizePolicy)
        self.adresIpEdit.setObjectName(_fromUtf8("adresIpEdit"))
        self.adresIpLayout.addWidget(self.adresIpEdit)
        self.verticalLayout.addLayout(self.adresIpLayout)
        self.numerPortuLayout = QtGui.QHBoxLayout()
        self.numerPortuLayout.setObjectName(_fromUtf8("numerPortuLayout"))
        self.numerPortuLbl = QtGui.QLabel(self.centralwidget)
        self.numerPortuLbl.setObjectName(_fromUtf8("numerPortuLbl"))
        self.numerPortuLayout.addWidget(self.numerPortuLbl)
        self.numerPortuEdit = QtGui.QLineEdit(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.numerPortuEdit.sizePolicy().hasHeightForWidth())
        self.numerPortuEdit.setSizePolicy(sizePolicy)
        self.numerPortuEdit.setObjectName(_fromUtf8("numerPortuEdit"))
        self.numerPortuLayout.addWidget(self.numerPortuEdit)
        self.verticalLayout.addLayout(self.numerPortuLayout)
        self.podlaczSieBtn = QtGui.QPushButton(self.centralwidget)
        self.podlaczSieBtn.setCheckable(False)
        self.podlaczSieBtn.setChecked(False)
        self.podlaczSieBtn.setObjectName(_fromUtf8("podlaczSieBtn"))
        self.verticalLayout.addWidget(self.podlaczSieBtn)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 699, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusbar.sizePolicy().hasHeightForWidth())
        self.statusbar.setSizePolicy(sizePolicy)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Warcoin", None))
        self.nrTuryLbl.setText(_translate("MainWindow", "Numer tury: ?", None))
        self.nowaTuraBtn.setText(_translate("MainWindow", "Nowa tura", None))
        self.nawiazanePolaczeniaLbl.setText(_translate("MainWindow", "Nawiązane połączenia:", None))
        self.rozlaczBtn.setText(_translate("MainWindow", "Rozłącz", None))
        self.adresIpLbl.setText(_translate("MainWindow", "Adres IP:", None))
        self.adresIpEdit.setText(_translate("MainWindow", "0.0.0.0", None))
        self.numerPortuLbl.setText(_translate("MainWindow", "Numer portu:", None))
        self.podlaczSieBtn.setText(_translate("MainWindow", "Podłącz się", None))

