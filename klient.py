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

def handle():
    global gniazdo, nr_tury, zglosilem, zglosil
    logging.info("Siedze tu.")
    while True:
        data = gniazdo.recv(1024).rstrip()
        logging.debug("k_data=%s" % data)
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

def podlacz_sie():
    global gniazdo, lineedit
    gniazdo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gniazdo.connect(("0.0.0.0", int(lineedit.text())))
    threading.Thread(target=handle).start()

if __name__=="__main__":
    
    app = QtGui.QApplication([])
    window = QtGui.QWidget()
    layout = QtGui.QVBoxLayout(window)
    window.setLayout(layout)
    btn = QtGui.QPushButton("No kurwa")
    btn2 = QtGui.QPushButton("Podlacz sie")

    btn.clicked.connect(lambda: ui())
    btn2.clicked.connect(lambda: podlacz_sie())
    lineedit = QtGui.QLineEdit()
    layout.addWidget(lineedit)
    layout.addWidget(btn2)
    layout.addWidget(btn)


    window.show()
    
    app.exec_()
    