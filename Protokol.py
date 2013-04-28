# -*- coding: utf-8 -*-

import logging
import SocketServer
import threading
import socket
import base64

from Crypto.Cipher import DES3

from Jednostka import Jednostka
import config as c

class Protokol(SocketServer.BaseRequestHandler):
    
    plansza = [ [None for _ in range(c.wielkosc_planszy)] for _ in range(c.wielkosc_planszy) ]
    nr_tury = 1
    zglosilem = False
    zglosil = False
    gniazdo = None
    okno = None
    port_nasluchu = None
    podlaczeni = []
    historia_gry = ""
    wolne_punkty = c.punkty_start
    zaszyfrowane = []
    czy_serwer = False
    jednostki = []
    
    @classmethod
    def wspolrzedne_gracza(self):
        if self.czy_serwer:
            return (c.wielkosc_planszy-1, c.wielkosc_planszy-1)
        else:
            return (0,0)
        
    @classmethod
    def wspolrzedne_przeciwnika(self):
        if not self.czy_serwer:
            return (c.wielkosc_planszy-1, c.wielkosc_planszy-1)
        else:
            return (0,0)
    
    @classmethod
    def rozpocznij_gre(self, czy_serwer):
        x, y = self.wspolrzedne_gracza()
        x2, y2 = self.wspolrzedne_przeciwnika()
        Jednostka.dopisz(self, x2, y2, False)
        Jednostka.dopisz(self, x, y, True)
            
    @classmethod
    def koniec_tury(self):
        self.dopisz(u"Przyjęto koniec tury.")
        logging.debug("KONIECTURY")
        self.zglosil = True
        if self.zglosilem:
            self.obsluz_nowa_ture()
            logging.debug("Nowa tura, nr=%s" % self.nr_tury)
            
    @classmethod
    def kup_jednostke(self):
        x, y = self.wspolrzedne_gracza()
        if self.plansza[x][y] is not None:
            raise Exception(u"Róg planszy zajęty.")
        Jednostka.dopisz(self, x, y, True)
        self.wolne_punkty -= c.koszt_kupna
        self.dopisz(u"Kupiono jednostkę.")
        self.gniazdo.send("KUPUJE")
    
    @classmethod
    def nadaj_zaszyfrowana(self, komunikat, x, y):
        zero_pad = lambda tekst: tekst + '\0' * (8 - len(tekst) % 8)
        des3 = DES3.new(self.plansza[x][y].klucz_szyfrujacy, DES3.MODE_CBC , '12345678')
        zaszyfrowane = des3.encrypt(zero_pad(komunikat))
        self.gniazdo.send("ZASZYFROWANE %s" % base64.encodestring(zaszyfrowane))
    
    @classmethod
    def dodaj_punkt(self, x, y):
        self.plansza[x][y].dodaj_punkt()
        self.wolne_punkty -= 1
        self.nadaj_zaszyfrowana("PRZELEJ %s %s" % (x, y), x, y)
        self.dopisz("Przelano punkty do (%s, %s)" % (x, y))
        
    @classmethod
    def zabierz_punkt(self, x, y):
        self.plansza[x][y].zabierz_punkt()
        self.wolne_punkty += 1
        self.nadaj_zaszyfrowana("ZABIERZ %s %s" % (x, y), x, y)
        self.dopisz("Zabrano punkty z (%s, %s)" % (x, y))
    
    @classmethod
    def przesun(self, komenda):
        s_x, s_y, x, y = map(int, komenda[1:])
        self.dopisz(u"Przeciwnik sie przesunął: %s,%s->%s,%s" % (s_x, s_y, x, y))
        self.plansza[s_x][s_y].przesun(x,y)
    
    @classmethod
    def odczytuj(self, czy_serwer=True):
        self.czy_serwer = czy_serwer
        self.rozpocznij_gre(czy_serwer)
        if self.gniazdo is None:
            self.gniazdo = self.request
        logging.info("Siedze tu.")
        while True:
            data = self.gniazdo.recv(1024).rstrip()
            # logging.debug("k_data=%s" % data)
            komenda = data.split(' ')
            if komenda == [] or komenda == ['']:
                continue
            if komenda[0] == 'KONIECTURY':
                self.koniec_tury()
            elif komenda[0] == "PRZESUN":
                self.przesun(komenda)
            elif komenda[0] == "ZASZYFROWANE":
                self.dopisz(u"Odebrano (zaszyfrowane)")
                self.zaszyfrowane += komenda[1]
            elif komenda[0] == "KUPUJE":
                x, y = self.wspolrzedne_przeciwnika()
                Jednostka.dopisz(self, x, y, False)
                self.dopisz(u"Przeciwnik kupił jednostkę.")
            elif komenda[0] == "ODSZYFRUJE":
                self.dopisz(u"Wojna. Odebrano szyfr.")
                self.obsluz_wojne(komenda[1])
            else:
                logging.error("Nieznana komenda: '%s'" % komenda[0])
                
    @classmethod
    def obsluz_wojne(self, szyfr):
        self.dopisz(u"Niestety, na razie not implemented.")

    @classmethod
    def wyslij_przesun(self, stary_pos, nowy_pos):
        s_x, s_y = stary_pos 
        x, y = nowy_pos
        self.gniazdo.send("PRZESUN %s %s %s %s" % (s_x, s_y, x, y))
        self.dopisz(u"Przesunięto się: %s,%s->%s,%s" % (s_x, s_y, x, y))
    
    def handle(self):
        Protokol.gniazdo = self.request
        host, port = self.client_address
        Protokol.podlaczeni += [("K", host, port)]
        self.dopisz(u"Przyjęto połączenie od %s:%s" % (host, port))
        Protokol.odczytuj(False)
    
    @classmethod
    def obsluz_nowa_ture(self):
        self.nr_tury += 1
        self.zglosil = False
        self.zglosilem = False
        self.wolne_punkty += c.bonus_tury
        for jednostka in self.jednostki:
            if not jednostka.obok_przeciwnik():
                jednostka.wykonano_ruch = False
            else:
                #mamy wojne
                self.odszyfruj(jednostka)
    
    @classmethod
    def odszyfruj(self, jednostka):
        self.gniazdo.send("ODSZYFRUJE %s" % base64.encodestring(jednostka.klucz_szyfrujacy))
            
     
    @classmethod               
    def nowa_tura(self):
        self.dopisz(u"Ogłoszono koniec tury.")
        logging.debug("Wysylam")
        self.zglosilem = True
        self.gniazdo.send("KONIECTURY")
        if self.zglosil:
            self.obsluz_nowa_ture()
            logging.debug("Nowa tura, nr=%s" % self.nr_tury)
            
    @classmethod
    def podlacz_sie(self, host, port):
        Protokol.gniazdo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Protokol.gniazdo.connect((host, port))
        self.podlaczeni += [("S", host, port)]
        self.dopisz(u"Podłączono do %s:%s" % (host, port))
        threading.Thread(target=Protokol.odczytuj).start()
        
    @classmethod
    def dopisz(self, tekst):
        self.historia_gry += "%s\n" % tekst
        
    @classmethod
    def uruchom_serwer(self):
        port = 4000
        while True:
            try:
                logging.info("Proboje port %s" % port)
                server = SocketServer.TCPServer(("0.0.0.0", port), Protokol)
                Protokol.port_nasluchu = port
                logging.info("Sukces.")
                break
            except socket.error:
                port += 1
        t = threading.Thread(target=lambda:server.serve_forever())
        t.start()
