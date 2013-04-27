# -*- coding: utf-8 -*-

import logging
import SocketServer
import threading
import socket

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
    
    @classmethod
    def rozpocznij_gre(self, czy_serwer):
        if czy_serwer:
            self.plansza[0][0] = "X"
            self.plansza[4][4] = "!"
        else:
            self.plansza[0][0] = "!"
            self.plansza[4][4] = "X"
            
    @classmethod
    def koniec_tury(self):
        self.dopisz(u"Przyjęto koniec tury.")
        logging.debug("KONIECTURY")
        self.zglosil = True
        if self.zglosilem:
            self.nr_tury += 1
            self.zglosilem = False
            self.zglosil = False
            logging.debug("Nowa tura, nr=%s" % self.nr_tury)
    
    @classmethod
    def przesun(self, komenda):
        s_x, s_y, x, y = map(int, komenda[1:])
        self.dopisz(u"Przeciwnik sie przesunął: %s,%s->%s,%s" % (s_x, s_y, x, y))
        self.dopisz(u"Koniec tury.")
        self.plansza[s_x][s_y] = None
        self.plansza[x][y] = "X"
    
    @classmethod
    def odczytuj(self, czy_serwer = True):
        self.rozpocznij_gre(czy_serwer)
        if self.gniazdo is None:
            self.gniazdo = self.request
        logging.info("Siedze tu.")
        while True:
            data = self.gniazdo.recv(1024).rstrip()
            #logging.debug("k_data=%s" % data)
            komenda = data.split(' ')
            if komenda[0]=='KONIECTURY':
                self.koniec_tury()
            if komenda[0]=="PRZESUN":
                self.przesun(komenda)

    @classmethod
    def wyslij_przesun(self, stary_pos, nowy_pos):
        s_x, s_y = stary_pos 
        x, y = nowy_pos
        self.gniazdo.send("PRZESUN %s %s %s %s" % ( s_x, s_y, x, y))
        self.dopisz(u"Przesunięto się: %s,%s->%s,%s" % (s_x, s_y, x, y))
    
    def handle(self):
        Protokol.gniazdo = self.request
        host, port = self.client_address
        Protokol.podlaczeni += [("K", host, port)]
        self.dopisz(u"Przyjęto połączenie od %s:%s" % (host, port))
        Protokol.odczytuj(False)
     
    @classmethod               
    def nowa_tura(self):
        self.dopisz(u"Ogłoszono koniec tury.")
        logging.debug("Wysylam")
        self.zglosilem = True
        self.gniazdo.send("KONIECTURY")
        if self.zglosil:
            self.nr_tury += 1
            self.zglosil = False
            self.zglosilem = False
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
