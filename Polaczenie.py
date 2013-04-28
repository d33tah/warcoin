# -*- coding: utf-8 -*-

import logging
import SocketServer
import threading
import socket
import base64

from Crypto.Cipher import DES3

from Gra import Gra
import config as c

class Polaczenie(SocketServer.BaseRequestHandler):
    
    port_nasluchu = None
    podlaczeni = []
    jednostki = []
    gra = None

    def handle(self):
        host, port = self.client_address
        if self.server:
            typ = "S"
            self.gra.dopisz(u"Przyjęto połączenie od %s:%s" % (host, port))
        else:
            typ = "K"
            self.gra.dopisz(u"Podłączono do %s:%s" % (host, port))
        self.podlaczeni += [(typ, host, port)]
        
        self.odczytuj()
    
    def setup(self):
        logging.critical("HACK: PolaczenieTymczasowy.setup()")
        self.gra = Gra.instance()
        self.gra.polaczenie = self
    

    @classmethod
    def uruchom_serwer(self):
                    
        port = 4000
        while True:
            try:
                logging.info("Proboje port %s" % port)
                
                # ta linijka rzuci socket error, jeśli port jest już zajęty.
                server = SocketServer.TCPServer(("0.0.0.0", port), Polaczenie)
                Polaczenie.port_nasluchu = port
                                
                logging.info("Sukces.")
                break
            except socket.error:
                port += 1
        t = threading.Thread(target=lambda:server.serve_forever())
        t.start()

    @classmethod
    def podlacz_sie(cls, host, port):

        logging.critical("HACK: PolaczenieTymczasowy")
        gniazdo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        gniazdo.connect((host, port))
        cls.podlaczeni += [("S", host, port)]
        threading.Thread(target=lambda: Polaczenie(request=gniazdo,
                                                   client_address=(host, port),
                                                   server=None)).start()
    


    def odczytuj(self):
        
        if self.server:
            wspolrzedne_gracza = (c.wielkosc_planszy - 1, c.wielkosc_planszy - 1) 
            wspolrzedne_wroga = (0, 0)
        else:
            wspolrzedne_wroga = (c.wielkosc_planszy - 1, c.wielkosc_planszy - 1) 
            wspolrzedne_gracza = (0, 0)
            
        self.gra.rozpocznij_gre(wspolrzedne_gracza, wspolrzedne_wroga)
        
        logging.info("Polaczenie.odczytuj")
        while True:
            data = self.request.recv(1024).rstrip()
            # logging.debug("k_data=%s" % data)
            komenda = data.split(' ')
            if komenda == [] or komenda == ['']:
                continue
            if komenda[0] == 'KONIECTURY':
                self.gra.przyjmij_nowa_ture()
            elif komenda[0] == "PRZESUN":
                self.gra.przesun_wroga(*map(int, komenda[1:]))
            elif komenda[0] == "ZASZYFROWANE":
                self.gra.przyjmij_zaszyfrowane(komenda[1])
            elif komenda[0] == "KUPUJE":
                self.gra.przyjmij_kupno()
            elif komenda[0] == "ODSZYFRUJE":
                self.gra.przyjmij_wojne(komenda[1])
            else:
                logging.error("Nieznana komenda: '%s'" % komenda[0])
    
    def nadaj_zaszyfrowana(self, komunikat, x, y):
        zero_pad = lambda tekst: tekst + '\0' * (8 - len(tekst) % 8)
        des3 = DES3.new(self.gra.plansza[x][y].klucz_szyfrujacy, DES3.MODE_ECB,
                         '12345678')
        zaszyfrowane = des3.encrypt(zero_pad(komunikat))
        self.request.send("ZASZYFROWANE %s" % base64.encodestring(zaszyfrowane))
                

    def wyslij_przesun(self, s_x, s_y, x, y):
        self.request.send("PRZESUN %s %s %s %s" % (s_x, s_y, x, y))
    
    def odkryj_szyfr(self, jednostka):
        zakodowany_klucz = base64.encodestring(jednostka.klucz_szyfrujacy)
        self.request.send("ODSZYFRUJE %s" % zakodowany_klucz)

    def wyslij_dodaj(self, x, y):
        self.nadaj_zaszyfrowana("PRZELEJ %s %s" % (x, y), x, y)

    def wyslij_zabierz(self, x, y):
        self.nadaj_zaszyfrowana("ZABIERZ %s %s" % (x, y), x, y)
    
    def wyslij_kup(self):        
        self.request.send("KUPUJE")

    def wyslij_nowa_ture(self):
        self.request.send("KONIECTURY")

