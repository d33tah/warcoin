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
    
    gniazdo = None
    port_nasluchu = None
    podlaczeni = []
    zaszyfrowane = []
    jednostki = []
    gra = None
       
    @classmethod
    def uruchom_serwer(self):
        port = 4000
        while True:
            try:
                logging.info("Proboje port %s" % port)
                server = SocketServer.TCPServer(("0.0.0.0", port), Protokol)
                self.port_nasluchu = port
                logging.info("Sukces.")
                break
            except socket.error:
                port += 1
        t = threading.Thread(target=lambda:server.serve_forever())
        t.start()

    @classmethod
    def podlacz_sie(self, host, port):
        self.gniazdo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gniazdo.connect((host, port))
        self.podlaczeni += [("S", host, port)]
        self.gra.dopisz(u"Podłączono do %s:%s" % (host, port))
        threading.Thread(target=self.odczytuj).start()
    
    def handle(self):
        Protokol.gniazdo = self.request
        host, port = self.client_address
        self.podlaczeni += [("K", host, port)]
        self.gra.dopisz(u"Przyjęto połączenie od %s:%s" % (host, port))
        logging.critical("HACK: Protokol.odczytuj(False), uważać przy zmianie.")
        Protokol.odczytuj(False)

    @classmethod
    def odczytuj(self, czy_serwer=True):
        self.czy_serwer = czy_serwer
        
        if czy_serwer:
            wspolrzedne_gracza = (c.wielkosc_planszy-1, c.wielkosc_planszy-1) 
            wspolrzedne_wroga = (0, 0)
        else:
            wspolrzedne_wroga = (c.wielkosc_planszy-1, c.wielkosc_planszy-1) 
            wspolrzedne_gracza = (0, 0)
            
        self.gra.rozpocznij_gre(czy_serwer, wspolrzedne_gracza, wspolrzedne_wroga)
        
        #if self.gniazdo is None:
        #    self.gniazdo = self.request
        
        logging.info("Siedze tu.")
        while True:
            data = self.gniazdo.recv(1024).rstrip()
            # logging.debug("k_data=%s" % data)
            komenda = data.split(' ')
            if komenda == [] or komenda == ['']:
                continue
            if komenda[0] == 'KONIECTURY':
                self.gra.przyjmij_nowa_ture()
            elif komenda[0] == "PRZESUN":
                self.gra.przesun_wroga(*map(int, komenda[1:]))
            elif komenda[0] == "ZASZYFROWANE":
                self.gra.dopisz(u"Odebrano (zaszyfrowane)")
                self.zaszyfrowane += komenda[1]
            elif komenda[0] == "KUPUJE":
                x, y = self.wspolrzedne_przeciwnika()
                Jednostka.dopisz(self, x, y, False)
                self.gra.dopisz(u"Przeciwnik kupił jednostkę.")
            elif komenda[0] == "ODSZYFRUJE":
                self.gra.przyjmij_wojne(komenda[1])
            else:
                logging.error("Nieznana komenda: '%s'" % komenda[0])
    
    @classmethod
    def nadaj_zaszyfrowana(self, komunikat, x, y):
        zero_pad = lambda tekst: tekst + '\0' * (8 - len(tekst) % 8)
        des3 = DES3.new(self.gra.plansza[x][y].klucz_szyfrujacy, DES3.MODE_CBC , '12345678')
        zaszyfrowane = des3.encrypt(zero_pad(komunikat))
        self.gniazdo.send("ZASZYFROWANE %s" % base64.encodestring(zaszyfrowane))
                

    @classmethod
    def wyslij_przesun(self, s_x, s_y, x, y):
        self.gniazdo.send("PRZESUN %s %s %s %s" % (s_x, s_y, x, y))
    
    @classmethod
    def odkryj_szyfr(self, jednostka):
        self.gniazdo.send("ODSZYFRUJE %s" % base64.encodestring(jednostka.klucz_szyfrujacy))

    @classmethod
    def wyslij_dodaj(self, x, y):
        self.nadaj_zaszyfrowana("PRZELEJ %s %s" % (x, y), x, y)

    @classmethod
    def wyslij_zabierz(self, x, y):
        self.nadaj_zaszyfrowana("ZABIERZ %s %s" % (x, y), x, y)
    
    @classmethod
    def wyslij_kup(self):        
        self.gniazdo.send("KUPUJE")

    @classmethod
    def wyslij_nowa_ture(self):
        self.gniazdo.send("KONIECTURY")

