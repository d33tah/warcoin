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
from Polaczenie import Polaczenie
import config as c

class Okienko(QtGui.QMainWindow):
    
    polsingleton = None

    @classmethod
    def instance(cls):
        if cls.polsingleton is None:
            cls.polsingleton = cls()
        return cls.polsingleton
    
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        self.gra = Gra.instance()
        
        #w ten sposób ten kod uruchomi się także pod Python Portable, gdzie
        #nie ma uic.
        global got_uic
        if got_uic:
            Ui_MainWindow = uic.loadUiType("ui/mainwindow.ui")[0]
            self.ui = Ui_MainWindow()
        else:
            self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
            
        self.timer = QtCore.QTimer()
        self.ui.nrTuryLbl.connect(self.timer, QtCore.SIGNAL('timeout()'), 
                                  self.odswiez_ekran)
        self.timer.start(1000)
        
        self.tryb_przyciskow = None
        self.ruch_z = None
        
        self.stworz_przyciski()
        
        self.ui.podlaczSieBtn.clicked.connect(lambda: self.podlacz_sie())
        self.ui.nowaTuraBtn.clicked.connect(lambda: self.gra.nowa_tura())
        self.ui.przelejPunktyBtn.clicked.connect(self.przelej_punkty)
        self.ui.zabierzPunktyBtn.clicked.connect(self.zabierz_punkty)
        self.ui.kupJednostkeBtn.clicked.connect(self.kup_jednostke)
    
    def stworz_przyciski(self):
        pionowo = QtGui.QVBoxLayout()
        self.ui.widget.setLayout(pionowo)
        self.przyciski = [ [None for _ in range(c.wielkosc_planszy)] 
                          for _ in range(c.wielkosc_planszy) ]
        for y in range(c.wielkosc_planszy):
            poziomo = QtGui.QHBoxLayout()
            for x in range(c.wielkosc_planszy):
                wdg = QtGui.QPushButton()
                """
                HACK - tworzymy wyrażenie lambda, które bierze trzy zmienne.
                Pierwszy jest potrzebny, żeby hack ruszył, dwa pozostałe
                sprawią, że interpreter nie "spłaszczy" tego wyrażenia mimo,
                że jest w pętli. W ten sposób w każdej iteracji tworzone jest
                nowe - argumenty mają swoje wartości domyślne, więc całość
                zadziała bez problemu przy clicked.
                """
                wdg.clicked.connect(lambda wdg=wdg, x=x, y=y: 
                                    self.wcisnieto_przycisk(x, y))
                poziomo.addWidget(wdg)
                self.przyciski[x][y] = wdg
            pionowo.addLayout(poziomo)

    def blad(self, err):
        QtGui.QMessageBox.critical(self, u'Błąd', err, QtGui.QMessageBox.Ok, 
                                                  QtGui.QMessageBox.Ok)
        
    def przelej_punkty(self):
        self.tryb_przyciskow = "PRZELEJ"
        
    def zabierz_punkty(self):
        self.tryb_przyciskow = "ZABIERZ"

    def kup_jednostke(self):
        x, y = self.gra.gracz.wspolrzedne
        if self.gra.plansza[x][y] is not None:
            self.blad(u'Błąd', u"Róg planszy zajęty.")
        elif self.gra.wolne_punkty < c.koszt_kupna:
            self.blad(u"Nie masz tyle punktów.")
        else:
            self.gra.kup_jednostke()
            
            
    def wcisnieto_przycisk(self, x, y):
        """
        Do tej funkcji poprzez wyrażenie lambda są podpięte wygenerowane
        w konstruktorze okna przyciski.
        
        Zachowanie funkcji zmienia self.tryb_przyciskow, ustawiany przez
        przyciski "Kup", "Przelej", "Zabierz" - domyślnie, kliknięcie na button
        powoduje oznaczenie jednostki jako źródła przesunięcia, następne - celu.
        """
        
        logging.critical("HACK: refaktorowac wcisnieto_przycisk. "
                         "Wszystkie warunki powinny być sprawdzane po stronie"
                         " protokołu.")
        jednostka = self.gra.plansza[x][y]
        if isinstance(jednostka, Jednostka) and jednostka.czyja:
            nasza = True
        else:
            nasza = False
            
        if self.tryb_przyciskow is None:
            if nasza:
                if jednostka.wykonano_ruch:
                    self.blad(u"Wykonałeś już ruch tą jednostką!")
                elif jednostka.ile_hp > 1:
                    self.ruch_z = (x, y)
                    self.tryb_przyciskow = "PRZESUN"
                else:
                    self.blad(u"Wojska tutaj nie mają wystarczająco punktów!")
            else:
                self.blad(u"Tu nie ma twoich wojsk!")
                
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
                self.blad(u"Niedozwolony ruch: %s,%s" % (x, y))
                
        elif self.tryb_przyciskow == "PRZELEJ":
            if self.gra.wolne_punkty > 0:
                if nasza:
                    self.gra.dodaj_punkt(x, y)
                else:
                    self.blad(u"Tu nie ma twoich wojsk!")
            else:
                self.blad(u"Brak wolnych punktów!")
            self.tryb_przyciskow = None
            
        elif self.tryb_przyciskow == "ZABIERZ":
            if nasza:
                if jednostka.ile_hp > 1:
                    self.gra.zabierz_punkt(x, y)
                else:
                    self.blad(u"Jednostka ma za mało punktów!")
            else:
                self.blad(u"Tu nie ma twoich wojsk!")
            self.tryb_przyciskow = None
            
        else:
            self.blad(u"Nie zaimplementowano.")
    
    def podlacz_sie(self):
        try:
            Polaczenie.podlacz_sie(self.ui.adresIpEdit.text(), 
                                   int(self.ui.numerPortuEdit.text()))
        except socket.error, e:
            self.blad(unicode(e))
            self.ui.statusbar.showMessage(str(e))

    def odswiez_historie(self):
        self.ui.historiaGryEdit.setText(self.gra.historia_gry)
        cur = self.ui.historiaGryEdit.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        self.ui.historiaGryEdit.setTextCursor(cur)

    def odswiez_przyciski(self):
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
                
    def odswiez_ekran(self):
        self.odswiez_historie()
        self.odswiez_przyciski()
                
        if Polaczenie.port_nasluchu:
            self.statusBar().showMessage(u"Nasłuchuję na porcie %s" % 
                                         Polaczenie.port_nasluchu)
                
        if self.gra.polaczenie is not None:
            self.ui.panelGry.setEnabled(not self.gra.gracz.zglosil_ture)
            self.ui.przelejPunktyBtn.setEnabled(self.gra.wolne_punkty > 0)
            self.ui.nrTuryLbl.setText(u"Numer tury: %s" % self.gra.nr_tury)
            self.ui.pozostaloPunktowLbl.setText(u"Pozostało punktów: %s" % 
                                                self.gra.wolne_punkty)
            self.ui.peerList.clear()
            for gniazdo in self.gra.polaczenie.podlaczeni:
                self.ui.peerList.addItem("(%s) %s:%s" % gniazdo)
            
