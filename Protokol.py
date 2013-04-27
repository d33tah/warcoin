# -*- coding: utf-8 -*-

import logging
import SocketServer
import threading
import socket
import base64
import random
from Crypto.Cipher import DES3

class Protokol(SocketServer.BaseRequestHandler):
    
    plansza = [ [None for _ in range(5)] for _ in range(5) ]
    nr_tury = 0
    zglosilem = False
    zglosil = False
    gniazdo = None
    okno = None
    port_nasluchu = None
    podlaczeni = []
    historia_gry = ""
    wolne_punkty = 1
    zaszyfrowane = []
    klucz_szyfrujacy = ''.join([ chr(random.randint(0, 255)) for i in range(16)])
    
    @classmethod
    def rozpocznij_gre(self, czy_serwer):
        if czy_serwer:
            self.plansza[0][0] = "?"
            self.plansza[4][4] = 1
        else:
            self.plansza[0][0] = 1
            self.plansza[4][4] = "?"
            
    @classmethod
    def koniec_tury(self):
        self.dopisz(u"Przyjęto koniec tury.")
        logging.debug("KONIECTURY")
        self.zglosil = True
        if self.zglosilem:
            self.obsluz_nowa_ture()
            logging.debug("Nowa tura, nr=%s" % self.nr_tury)
    
    @classmethod
    def dodaj_punkt(self, x, y):
        self.plansza[x][y] += 1
        self.wolne_punkty -= 1
        zero_pad = lambda tekst: tekst + '\0' * (8 - len(tekst) % 8)
        des3 = DES3.new(self.klucz_szyfrujacy, DES3.MODE_CBC , '12345678')
        zaszyfrowane = des3.encrypt(zero_pad("PRZELEJ %s %s" % (x, y)))
        self.gniazdo.send("ZASZYFROWANE %s" % base64.encodestring(zaszyfrowane))
    
    @classmethod
    def przesun(self, komenda):
        s_x, s_y, x, y = map(int, komenda[1:])
        self.dopisz(u"Przeciwnik sie przesunął: %s,%s->%s,%s" % (s_x, s_y, x, y))
        self.plansza[s_x][s_y] = None
        self.plansza[x][y] = "X"
    
    @classmethod
    def odczytuj(self, czy_serwer=True):
        self.rozpocznij_gre(czy_serwer)
        if self.gniazdo is None:
            self.gniazdo = self.request
        logging.info("Siedze tu.")
        while True:
            data = self.gniazdo.recv(1024).rstrip()
            # logging.debug("k_data=%s" % data)
            komenda = data.split(' ')
            if komenda == []:
                continue
            if komenda[0] == 'KONIECTURY':
                self.koniec_tury()
            elif komenda[0] == "PRZESUN":
                self.przesun(komenda)
            elif komenda[0] == "ZASZYFROWANE":
                logging.error("Odebralem zaszyfrowane: %s, %s" % (komenda, komenda[1]))
                self.zaszyfrowane += komenda[1]
            else:
                logging.error("Nieznana komenda:" % komenda[0])

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
        self.wolne_punkty += 1
     
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
