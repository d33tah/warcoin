import logging
import SocketServer
import threading
import socket
from PyQt4 import QtCore


class Protokol(SocketServer.BaseRequestHandler):
    
    plansza = [ [None for _ in range(10)] for _ in range(10) ]
    nr_tury = 0
    zglosilem = False
    zglosil = False
    gniazdo = None
    okno = None
    port_nasluchu = None
    podlaczeni = []
    
    @classmethod
    def odczytuj(self):
        if self.gniazdo is None:
            self.gniazdo = self.request
        logging.info("Siedze tu.")
        while True:
            data = self.gniazdo.recv(1024).rstrip()
            logging.debug("k_data=%s" % data)
            komenda = data.split(' ')
            if komenda[0]=='KONIECTURY':
                logging.debug("KONIECTURY")
                self.zglosil = True
                if self.zglosilem:
                    self.nr_tury += 1
                    self.zglosilem = False
                    self.zglosil = False
                    logging.debug("Nowa tura, nr=%s" % self.nr_tury)

    
    def handle(self):
        Protokol.gniazdo = self.request
        Protokol.podlaczeni += [self]
        Protokol.odczytuj()
     
    @classmethod               
    def nowa_tura(self):
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
        threading.Thread(target=Protokol.odczytuj).start()
        
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
