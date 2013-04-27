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
        
        self.tryb_przyciskow = None
        self.ruch_z = None
        
        self.ui.podlaczSieBtn.clicked.connect(lambda: self.podlacz_sie())
        self.ui.nowaTuraBtn.clicked.connect(lambda: Protokol.nowa_tura())
        
        pionowo = QtGui.QVBoxLayout()
        self.rozmiar_planszy = 5
        self.ui.widget.setLayout(pionowo)
        self.przyciski = [ [None for _ in range(self.rozmiar_planszy)] for _ in range(self.rozmiar_planszy) ]
        for y in range(self.rozmiar_planszy):
            poziomo = QtGui.QHBoxLayout()
            for x in range(self.rozmiar_planszy):
                wdg = QtGui.QPushButton()
                wdg.clicked.connect(lambda wdg=wdg, x=x, y=y: self.wcisnieto_przycisk(x, y))
                poziomo.addWidget(wdg)
                self.przyciski[x][y] = wdg
            pionowo.addLayout(poziomo)
            
    def wcisnieto_przycisk(self, x, y):
        
        if self.tryb_przyciskow is None:
            if Protokol.plansza[x][y] == '!':
                self.ruch_z = (x, y)
                self.tryb_przyciskow = "PRZESUN"
            else:
                QtGui.QMessageBox.critical(self, u'Błąd', "Tu nie ma twoich wojsk!", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        elif self.tryb_przyciskow == "PRZESUN":
            stary_x, stary_y = self.ruch_z
            if y == stary_y and (x == stary_x + 1 or x == stary_x - 1) or \
                    x == stary_x and (y == stary_y + 1 or y == stary_y - 1):
                Protokol.wyslij_przesun(self.ruch_z, (x, y))
                Protokol.plansza[stary_x][stary_y] = None
                Protokol.plansza[x][y] = "!"
                self.tryb_przyciskow = None
            else:
                QtGui.QMessageBox.critical(self, u'Błąd', "Niedozwolony ruch: %s,%s" % (x, y), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            

    
    def podlacz_sie(self):
        try:
            Protokol.podlacz_sie(self.ui.adresIpEdit.text(), int(self.ui.numerPortuEdit.text()))
        except socket.error, e:
            QtGui.QMessageBox.critical(self, u'Błąd', unicode(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            self.ui.statusbar.showMessage(str(e))
    
    def odswiez_ekran(self):
        
        self.ui.historiaGryEdit.setText(Protokol.historia_gry)
        cur = self.ui.historiaGryEdit.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        self.ui.historiaGryEdit.setTextCursor(cur)
        for x in range(self.rozmiar_planszy):
            for y in range(self.rozmiar_planszy):
                pkt = Protokol.plansza[x][y]
                self.przyciski[x][y].setText('' if pkt is None else pkt) 
        
        if Protokol.gniazdo:
            self.ui.panelGry.setEnabled(not Protokol.zglosilem)
            self.ui.nrTuryLbl.setText("Numer tury: %s" % Protokol.nr_tury)
        if Protokol.port_nasluchu:
            self.statusBar().showMessage(u"Nasłuchuję na porcie %s" % Protokol.port_nasluchu)
            
        self.ui.peerList.clear()
        for gniazdo in Protokol.podlaczeni:
            self.ui.peerList.addItem("(%s) %s:%s" % gniazdo)
            
