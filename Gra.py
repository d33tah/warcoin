# -*- coding: utf-8 -*-

import logging

from Jednostka import Jednostka
from Protokol import Protokol
import config as c
from Gracz import Gracz

class Gra:
    
    plansza = [ [None for _ in range(c.wielkosc_planszy)] for _ in range(c.wielkosc_planszy) ]
    nr_tury = 1
    historia_gry = ""
    wolne_punkty = c.punkty_start
    jednostki = []
    protokol = Protokol
    
    gracz = None
    przeciwnik = None
    
    @classmethod
    def wspolrzedne_gracza(self):
        return self.gracz.wspolrzedne
        
    @classmethod
    def wspolrzedne_przeciwnika(self):
        return self.przeciwnik.wspolrzedne
    
    @classmethod
    def rozpocznij_gre(self, czy_serwer, wspolrzedne_gracza, wspolrzedne_przeciwnika):
        self.gracz = Gracz(wspolrzedne_gracza)
        self.przeciwnik = Gracz(wspolrzedne_przeciwnika)
        x, y = self.wspolrzedne_gracza()
        x2, y2 = self.wspolrzedne_przeciwnika()
        Jednostka.dopisz(self, x2, y2, False)
        Jednostka.dopisz(self, x, y, True)
    
    @classmethod
    def przesun_nasza(self, s_x, s_y, x, y):
        self.dopisz(u"Przesunięto się: %s,%s->%s,%s" % (s_x, s_y, x, y))
        self.protokol.wyslij_przesun(s_x, s_y, x, y)
    
    @classmethod
    def przesun_wroga(self, s_x, s_y, x, y):
        self.dopisz(u"Przeciwnik sie przesunął: %s,%s->%s,%s" % (s_x, s_y, x, y))
        self.plansza[s_x][s_y].przesun(x,y)
        
    @classmethod
    def dopisz(self, tekst):
        self.historia_gry += "%s\n" % tekst
            
    @classmethod
    def kup_jednostke(self):
        x, y = self.wspolrzedne_gracza()
        if self.plansza[x][y] is not None:
            raise Exception(u"Róg planszy zajęty.")
        Jednostka.dopisz(self, x, y, True)
        self.wolne_punkty -= c.koszt_kupna
        self.protokol.wyslij_kup()
    
    @classmethod
    def dodaj_punkt(self, x, y):
        self.plansza[x][y].dodaj_punkt()
        self.wolne_punkty -= 1
        self.protokol.wyslij_dodaj(x, y)
        self.dopisz("Przelano punkty do (%s, %s)" % (x, y))
         
    @classmethod
    def zabierz_punkt(self, x, y):
        self.plansza[x][y].zabierz_punkt()
        self.wolne_punkty += 1
        self.dopisz("Zabrano punkty z (%s, %s)" % (x, y))
        self.protokol.wyslij_zabierz(x, y)
    
    @classmethod
    def przyjmij_wojne(self, szyfr):
        self.dopisz(u"Niestety, na razie not implemented.")

    @classmethod
    def obsluz_nowa_ture(self):
        self.nr_tury += 1
        self.przeciwnik.zglosil_ture = False
        self.gracz.zglosil_ture = False
        self.wolne_punkty += c.bonus_tury
        for jednostka in self.jednostki:
            if not jednostka.obok_przeciwnik():
                jednostka.wykonano_ruch = False
            else:
                #mamy wojne
                self.protokol.odkryj_szyfr(jednostka)
    
    @classmethod
    def przyjmij_nowa_ture(self):
        self.dopisz(u"Przyjęto koniec tury.")
        logging.debug("KONIECTURY")
        self.przeciwnik.zglosil_ture = True
        if self.gracz.zglosil_ture:
            self.obsluz_nowa_ture()
            logging.debug("Nowa tura, nr=%s" % self.nr_tury)
         
    @classmethod               
    def nowa_tura(self):
        self.dopisz(u"Ogłoszono koniec tury.")
        logging.debug("Wysylam")
        self.gracz.zglosil_ture = True
        self.protokol.wyslij_nowa_ture()
        if self.przeciwnik.zglosil_ture:
            self.obsluz_nowa_ture()
            logging.debug("Nowa tura, nr=%s" % self.nr_tury)

logging.critical("Paskudny hack na koncu gra.py!")
Protokol.gra = Gra
            