# -*- coding: utf-8 -*-

import logging
import base64

from Crypto.Cipher import DES3

from Jednostka import Jednostka
import config as c
from Gracz import Gracz
from Rozkaz import Rozkaz, TypyRozkazow

class Gra:
    
    polsingleton = None

    @classmethod
    def instance(cls):
        if cls.polsingleton is None:
            cls.polsingleton = cls()
        return cls.polsingleton

    
    def __init__(self):
        self.plansza = [ [None for _ in range(c.wielkosc_planszy)] 
                        for _ in range(c.wielkosc_planszy) ]
        self.nr_tury = 1
        self.historia_gry = ""
        self.wolne_punkty = c.punkty_start
        self.jednostki = []
        self.rozkazy = []
        
        self.polaczenie = None
        
        self.gracz = None
        self.przeciwnik = None
    
    def rozpocznij_gre(self, czy_serwer, wspolrzedne_gracza, wspolrzedne_przeciwnika):
        self.gracz = Gracz(wspolrzedne_gracza)
        self.przeciwnik = Gracz(wspolrzedne_przeciwnika)
        x, y = wspolrzedne_gracza
        x2, y2 = wspolrzedne_przeciwnika
        Jednostka.dopisz(self, x2, y2, False)
        Jednostka.dopisz(self, x, y, True)
    
    def przesun_nasza(self, s_x, s_y, x, y):
        args = (s_x, s_y, x, y)
        self.rozkazy += [Rozkaz(self.gracz, TypyRozkazow.PRZESUN, args)]
        self.dopisz(u"Przesunięto się: %s,%s->%s,%s" % args)
        self.polaczenie.wyslij_przesun(*args)
    
    def przesun_wroga(self, s_x, s_y, x, y):
        args = (s_x, s_y, x, y)
        self.rozkazy += [Rozkaz(self.przeciwnik, TypyRozkazow.PRZESUN, args)]
        self.dopisz(u"Przeciwnik sie przesunął: %s,%s->%s,%s" % args)
        self.plansza[s_x][s_y].przesun(x,y)
        
    def dopisz(self, tekst):
        self.historia_gry += "%s\n" % tekst
            
    def kup_jednostke(self):
        self.rozkazy += [Rozkaz(self.gracz, TypyRozkazow.KUP, [])]
        x, y = self.gracz.wspolrzedne
        if self.plansza[x][y] is not None:
            raise Exception(u"Róg planszy zajęty.")
        Jednostka.dopisz(self, x, y, True)
        self.wolne_punkty -= c.koszt_kupna
        self.polaczenie.wyslij_kup()
    
    def dodaj_punkt(self, x, y):
        self.rozkazy += [Rozkaz(self.gracz, TypyRozkazow.DODAJ_PUNKT, [x, y])]
        self.plansza[x][y].dodaj_punkt()
        self.wolne_punkty -= 1
        self.polaczenie.wyslij_dodaj(x, y)
        self.dopisz("Przelano punkty do (%s, %s)" % (x, y))
         
    def zabierz_punkt(self, x, y):
        self.rozkazy += [Rozkaz(self.gracz, TypyRozkazow.ZABIERZ_PUNKT, [x, y])]
        self.plansza[x][y].zabierz_punkt()
        self.wolne_punkty += 1
        self.dopisz("Zabrano punkty z (%s, %s)" % (x, y))
        self.polaczenie.wyslij_zabierz(x, y)
    
    def przyjmij_wojne(self, szyfr_base64):
        self.rozkazy += [Rozkaz(self.przeciwnik, TypyRozkazow.ODSZYFRUJ, [szyfr_base64])]
        self.dopisz(u"Niestety, na razie not implemented.")
        szyfr = base64.decodestring(szyfr_base64)
        des3 = DES3.new(szyfr, DES3.MODE_ECB, '12345678')
        for i in range(len(self.rozkazy)):
            if self.rozkazy[i].typ == TypyRozkazow.ZASZYFROWANE:
                odszyfrowane = des3.decrypt(base64.decodestring(self.rozkazy[i].argumenty[0])).rstrip('\0')
                logging.debug(odszyfrowane)
                if odszyfrowane.startswith('PRZELEJ'):
                    self.rozkazy[i].typ = TypyRozkazow.DODAJ_PUNKT
                elif odszyfrowane.startswith('ZABIERZ'):
                    self.rozkazy[i].typ = TypyRozkazow.ZABIERZ_PUNKT
                else:
                    continue
                self.rozkazy[i].argumenty = odszyfrowane.split(' ')[1:]
                logging.debug(self.rozkazy[i])
        logging.debug(self.rozkazy)

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
                self.polaczenie.odkryj_szyfr(jednostka)
    
    def przyjmij_nowa_ture(self):
        self.rozkazy += [Rozkaz(self.przeciwnik, TypyRozkazow.NOWA_TURA, [])]
        self.dopisz(u"Przyjęto koniec tury.")
        logging.debug("KONIECTURY")
        self.przeciwnik.zglosil_ture = True
        if self.gracz.zglosil_ture:
            self.obsluz_nowa_ture()
            logging.debug("Nowa tura, nr=%s" % self.nr_tury)
         
    def nowa_tura(self):
        self.rozkazy += [Rozkaz(self.gracz, TypyRozkazow.NOWA_TURA, [])]
        self.dopisz(u"Ogłoszono koniec tury.")
        logging.debug("Wysylam")
        self.gracz.zglosil_ture = True
        self.polaczenie.wyslij_nowa_ture()
        if self.przeciwnik.zglosil_ture:
            self.obsluz_nowa_ture()
            logging.debug("Nowa tura, nr=%s" % self.nr_tury)

    def przyjmij_zaszyfrowane(self, szyfr):
        self.dopisz(u"Odebrano (zaszyfrowane)")
        self.rozkazy += [Rozkaz(self.przeciwnik, TypyRozkazow.ZASZYFROWANE, [szyfr])]

    def przyjmij_kupno(self):
        x, y = self.przeciwnik.wspolrzedne
        self.rozkazy += [Rozkaz(self.przeciwnik, TypyRozkazow.KUP, [])]
        Jednostka.dopisz(self, x, y, False)
        self.dopisz(u"Przeciwnik kupił jednostkę.")
                