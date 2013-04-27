#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging


import sys
import socket

from PyQt4 import QtCore
from PyQt4 import QtGui

try:
    from PyQt4 import uic
    got_uic = True
except ImportError:
    from ui import mainwindow
    got_uic = False

from protokol2 import Protokol

logging.getLogger().setLevel(logging.DEBUG)


class TruEdit(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        global got_uic
        if got_uic:
            self.ui = uic.loadUi("ui/mainwindow.ui")
        else:
            self.ui = mainwindow.Ui_MainWindow()
            self.ui.setupUi(self)
            
        self.timer = QtCore.QTimer()
        self.ui.nrTuryLbl.connect(self.timer, QtCore.SIGNAL('timeout()'), self.odswiez_ekran)
        self.timer.start(1000)
        
        self.ui.podlaczSieBtn.clicked.connect(lambda: self.podlacz_sie())
    
    def podlacz_sie(self):
        try:
            Protokol.podlacz_sie("0.0.0.0", int(self.ui.numerPortuEdit.text()))
        except socket.error, e:
            QtGui.QMessageBox.critical(self, u'Błąd', unicode(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            self.statusBar().showMessage(str(e))
    
    def odswiez_ekran(self):
        if Protokol.gniazdo:
            self.ui.nrTuryLbl.setText("Numer tury: %s" % Protokol.nr_tury)
        if Protokol.port_nasluchu:
            self.statusBar().showMessage("Nasluchuje na porcie %s" % Protokol.port_nasluchu)    
    
    def show(self):
        global got_uic
        if got_uic:
            self.ui.show()
        else:
            QtGui.QMainWindow.show(self)
    
if __name__=="__main__":
    
    app = QtGui.QApplication(sys.argv)
    t = TruEdit()
    t.show()
    sys.exit(app.exec_())