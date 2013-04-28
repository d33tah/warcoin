# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui
import socket
import logging

try:
    from PyQt4 import uic
    got_uic = True
except ImportError:
    from ui import mainwindow
    got_uic = False

from Gra import Gra
from Jednostka import Jednostka
import config as c

class Okienko(QtGui.QMainWindow):
    
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        self.gra = Gra
        
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
        self.ui.nowaTuraBtn.clicked.connect(lambda: self.gra.nowa_tura())
        self.ui.przelejPunktyBtn.clicked.connect(self.przelej_punkty)
        self.ui.zabierzPunktyBtn.clicked.connect(self.zabierz_punkty)
        self.ui.kupJednostkeBtn.clicked.connect(self.kup_jednostke)
        
        pionowo = QtGui.QVBoxLayout()
        self.ui.widget.setLayout(pionowo)
        self.przyciski = [ [None for _ in range(c.wielkosc_planszy)] for _ in range(c.wielkosc_planszy) ]
        for y in range(c.wielkosc_planszy):
            poziomo = QtGui.QHBoxLayout()
            for x in range(c.wielkosc_planszy):
                wdg = QtGui.QPushButton()
                wdg.clicked.connect(lambda wdg=wdg, x=x, y=y: self.wcisnieto_przycisk(x, y))
                poziomo.addWidget(wdg)
                self.przyciski[x][y] = wdg
            pionowo.addLayout(poziomo)
    
    def przelej_punkty(self):
        self.tryb_przyciskow = "PRZELEJ"
        
    def zabierz_punkty(self):
        self.tryb_przyciskow = "ZABIERZ"

    def kup_jednostke(self):
        x, y = self.gra.gracz.wspolrzedne
        if self.gra.plansza[x][y] is not None:
            QtGui.QMessageBox.critical(self, u'Błąd', u"Róg planszy zajęty.", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        elif self.gra.wolne_punkty < c.koszt_kupna:
            QtGui.QMessageBox.critical(self, u'Błąd', u"Nie masz tyle punktów.", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        else:
            self.gra.kup_jednostke()
            
            
    def wcisnieto_przycisk(self, x, y):
        
        logging.critical("WAZNE: refaktorowac wcisnieto_przycisk. Wszystkie warunki powinny być sprawdzane po stronie protokołu.")
        jednostka = self.gra.plansza[x][y]
        if isinstance(jednostka, Jednostka) and jednostka.czyja:
            nasza = True
        else:
            nasza = False
            
        blad = lambda err: QtGui.QMessageBox.critical(self, u'Błąd', err, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            
        if self.tryb_przyciskow is None:
            if nasza:
                if jednostka.wykonano_ruch:
                    blad(u"Wykonałeś już ruch tą jednostką!")
                elif jednostka.ile_hp > 1:
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
                self.gra.przesun_nasza(stary_x, stary_x, x, y)
                stara = self.gra.plansza[stary_x][stary_y] 
                stara.przesun(x, y)
                stara.wykonano_ruch = True
                stara.zabierz_punkt()
                self.tryb_przyciskow = None
            else:
                blad(u"Niedozwolony ruch: %s,%s" % (x, y))
        elif self.tryb_przyciskow == "PRZELEJ":
            if self.gra.wolne_punkty > 0:
                if nasza:
                    self.gra.dodaj_punkt(x, y)
                else:
                    blad(u"Tu nie ma twoich wojsk!")
            else:
                blad(u"Brak wolnych punktów!")
            self.tryb_przyciskow = None
        elif self.tryb_przyciskow == "ZABIERZ":
            if nasza:
                if jednostka.ile_hp > 1:
                    self.gra.zabierz_punkt(x, y)
                else:
                    blad(u"Jednostka ma za mało punktów!")
            else:
                blad(u"Tu nie ma twoich wojsk!")
            self.tryb_przyciskow = None
        else:
            blad(u"Nie zaimplementowano.")
            

    
    def podlacz_sie(self):
        try:
            self.gra.protokol.podlacz_sie(self.ui.adresIpEdit.text(), int(self.ui.numerPortuEdit.text()))
        except socket.error, e:
            QtGui.QMessageBox.critical(self, u'Błąd', unicode(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            self.ui.statusbar.showMessage(str(e))
    
    def odswiez_ekran(self):
        
        self.ui.historiaGryEdit.setText(self.gra.historia_gry)
        cur = self.ui.historiaGryEdit.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        self.ui.historiaGryEdit.setTextCursor(cur)
        i = 1
        for x in range(c.wielkosc_planszy):
            for y in range(c.wielkosc_planszy):
                pkt = self.gra.plansza[x][y]
                if pkt is None:
                        text = '' 
                else:
                    text = "%s" % (str(pkt))
                    if pkt.czyja:
                        text += " (&%s)" % i
                        i += 1
                self.przyciski[x][y].setText(text)
                
        
        if self.gra.protokol.gniazdo:
            self.ui.panelGry.setEnabled(not self.gra.gracz.zglosil_ture)
            self.ui.przelejPunktyBtn.setEnabled(self.gra.wolne_punkty > 0)
            self.ui.nrTuryLbl.setText(u"Numer tury: %s" % self.gra.nr_tury)
            self.ui.pozostaloPunktowLbl.setText(u"Pozostało punktów: %s" % self.gra.wolne_punkty)
        if self.gra.protokol.port_nasluchu:
            self.statusBar().showMessage(u"Nasłuchuję na porcie %s" % self.gra.protokol.port_nasluchu)
            
        self.ui.peerList.clear()
        for gniazdo in self.gra.protokol.podlaczeni:
            self.ui.peerList.addItem("(%s) %s:%s" % gniazdo)
            
