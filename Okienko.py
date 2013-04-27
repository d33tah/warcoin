# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui
import socket

try:
    from PyQt4 import uic
    got_uic = True
except ImportError:
    from ui import mainwindow
    got_uic = False

from Protokol import Protokol

class Okienko(QtGui.QMainWindow):
    
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        
        global got_uic
        if got_uic:
            Ui_MainWindow = uic.loadUiType("ui/mainwindow.ui")[0]
            self.ui = Ui_MainWindow()
        else:
            self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
            
        self.timer = QtCore.QTimer()
        self.ui.nrTuryLbl.connect(self.timer, QtCore.SIGNAL('timeout()'), self.odswiez_ekran)
        self.timer.start(1000)
        
        self.ui.podlaczSieBtn.clicked.connect(lambda: self.podlacz_sie())
        self.ui.nowaTuraBtn.clicked.connect(lambda: Protokol.nowa_tura())
    
    def podlacz_sie(self):
        try:
            Protokol.podlacz_sie("0.0.0.0", int(self.ui.numerPortuEdit.text()))
        except socket.error, e:
            QtGui.QMessageBox.critical(self, u'Błąd', unicode(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            self.ui.statusbar.showMessage(str(e))
    
    def odswiez_ekran(self):
        if Protokol.gniazdo:
            self.ui.nrTuryLbl.setText("Numer tury: %s" % Protokol.nr_tury)
        if Protokol.port_nasluchu:
            self.statusBar().showMessage(u"Nasłuchuję na porcie %s" % Protokol.port_nasluchu)
