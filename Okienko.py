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
        self.protokol = Protokol
        
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
        self.ui.nowaTuraBtn.clicked.connect(lambda: self.protokol.nowa_tura())
        self.ui.przelejPunktyBtn.clicked.connect(self.przelej_punkty)
        
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
    
    def przelej_punkty(self):
        self.tryb_przyciskow = "PRZELEJ"
            
    def wcisnieto_przycisk(self, x, y):
        
        oznaczenie = self.protokol.plansza[x][y]
        if oznaczenie is not None and oznaczenie!="?":
            nasza_jednostka = True
        else:
            nasza_jednostka = False
        blad = lambda err: QtGui.QMessageBox.critical(self, u'Błąd', err, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            
        if self.tryb_przyciskow is None:
            oznaczenie = self.protokol.plansza[x][y]
            if oznaczenie is not None and oznaczenie!="?":
                if oznaczenie > 1:
                    self.ruch_z = (x, y)
                    self.tryb_przyciskow = "PRZESUN"
                else:
                    blad(u"Wojska tutaj nie mają wystarczająco punktów!")
            else:
                blad(u"Tu nie ma twoich wojsk!")
        elif self.tryb_przyciskow == "PRZESUN":
            stary_x, stary_y = self.ruch_z
            if y == stary_y and (x == stary_x + 1 or x == stary_x - 1) or \
                    x == stary_x and (y == stary_y + 1 or y == stary_y - 1):
                self.protokol.wyslij_przesun(self.ruch_z, (x, y))
                self.protokol.plansza[x][y] = self.protokol.plansza[stary_x][stary_y]-1
                self.protokol.plansza[stary_x][stary_y] = None
                self.tryb_przyciskow = None
            else:
                blad(u"Niedozwolony ruch: %s,%s" % (x, y))
        elif self.tryb_przyciskow == "PRZELEJ":
            if self.protokol.wolne_punkty > 0:
                if nasza_jednostka:
                    self.protokol.dodaj_punkt(x, y)
                else:
                    blad(u"Tu nie ma twoich wojsk!")
            else:
                blad(u"Brak wolnych punktów!")
            self.tryb_przyciskow = None
        else:
            blad(u"Nie zaimplementowano.")
            

    
    def podlacz_sie(self):
        try:
            self.protokol.podlacz_sie(self.ui.adresIpEdit.text(),int(self.ui.numerPortuEdit.text()))
        except socket.error, e:
            QtGui.QMessageBox.critical(self, u'Błąd', unicode(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            self.ui.statusbar.showMessage(str(e))
    
    def odswiez_ekran(self):
        
        self.ui.historiaGryEdit.setText(self.protokol.historia_gry)
        cur = self.ui.historiaGryEdit.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        self.ui.historiaGryEdit.setTextCursor(cur)
        for x in range(self.rozmiar_planszy):
            for y in range(self.rozmiar_planszy):
                pkt = self.protokol.plansza[x][y]
                self.przyciski[x][y].setText('' if pkt is None else str(pkt)) 
        
        if self.protokol.gniazdo:
            self.ui.panelGry.setEnabled(not self.protokol.zglosilem)
            self.ui.przelejPunktyBtn.setEnabled(self.protokol.wolne_punkty > 0)
            self.ui.nrTuryLbl.setText(u"Numer tury: %s" % self.protokol.nr_tury)
            self.ui.pozostaloPunktowLbl.setText(u"Pozostało punktów: %s" % self.protokol.wolne_punkty)
        if self.protokol.port_nasluchu:
            self.statusBar().showMessage(u"Nasłuchuję na porcie %s" % self.protokol.port_nasluchu)
            
        self.ui.peerList.clear()
        for gniazdo in self.protokol.podlaczeni:
            self.ui.peerList.addItem("(%s) %s:%s" % gniazdo)
            
