#!/usr/bin/python

from __future__ import print_function

import logging
import socket
import SocketServer
import threading
from PyQt4 import QtGui
from PyQt4 import QtCore

logging.getLogger().setLevel(logging.DEBUG)

plansza = [ [None for _ in range(10)] for _ in range(10) ]
nr_tury = 0
zglosilem = False
zglosil = False
gniazdo = None

class ProtokolSerwera(SocketServer.BaseRequestHandler):
    
    def handle(self):
        global gniazdo, nr_tury, zglosilem, zglosil
        logging.info("Siedze tu.")
        gniazdo = self.request
        while True:
            data = self.request.recv(1024).rstrip()
            logging.debug("s_data=%s" % data)
            komenda = data.split(' ')
            if komenda[0]=='KONIECTURY':
                logging.debug("KONIECTURY")
                zglosil = True
                if zglosilem:
                    nr_tury += 1
                    zglosilem = False
                    zglosil = False
                    logging.debug("Nowa tura, nr=%s" % nr_tury)
                

def ui():
    global gniazdo, zglosil, zglosilem, nr_tury
    zglosilem = True
    gniazdo.send("KONIECTURY")
    if zglosil:
        nr_tury += 1
        zglosil = False
        zglosilem = False
        logging.debug("Nowa tura, nr=%s" % nr_tury)

if __name__=="__main__":
    port = 4000
    while True:
        try:
            logging.info("Proboje port %s" % port)
            server = SocketServer.TCPServer(("0.0.0.0", port), ProtokolSerwera)
            logging.info("Sukces.")
            break
        except socket.error:
            port += 1
    t = threading.Thread(target=lambda:server.serve_forever())
    t.start()
    app = QtGui.QApplication([])
    window = QtGui.QWidget()
    layout = QtGui.QVBoxLayout(window)
    window.setLayout(layout)
    btn = QtGui.QPushButton("No kurwa")
    btn.clicked.connect(lambda: ui())
    layout.addWidget(btn)
    window.show()
    app.exec_()
    