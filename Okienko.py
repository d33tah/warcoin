from PyQt4 import QtGui
from PyQt4 import QtCore

from protokol2 import Protokol

class Okienko(QtGui.QMainWindow):
    def __init__(self):
        super(Okienko, self).__init__()
        
        widget = QtGui.QWidget()
        self.setCentralWidget(widget)
        
        self.layout = QtGui.QVBoxLayout()
        widget.setLayout(self.layout)
        
        self.label = QtGui.QLabel("Niepodlaczony.")
        self.timer = QtCore.QTimer()
        self.label.connect(self.timer, QtCore.SIGNAL('timeout()'), self.odswiez_ekran)
        self.timer.start(1000)

        self.port_podlaczenia = QtGui.QLineEdit()
        self.layout.addWidget(self.port_podlaczenia)
        
        self.podlacz_sie_btn = QtGui.QPushButton("Podlacz sie")
        self.podlacz_sie_btn.clicked.connect(lambda: self.podlacz_sie())
        self.layout.addWidget(self.podlacz_sie_btn)

        self.layout.addWidget(self.label)
        
        self.btn = QtGui.QPushButton("Koniec tury")
        self.btn.clicked.connect(lambda: Protokol.nowa_tura())
        self.layout.addWidget(self.btn)

        statusbar = QtGui.QStatusBar()
        self.setStatusBar(statusbar)
        self.statusBar().showMessage("Niepodlaczony.")
        
    def podlacz_sie(self):
        Protokol.podlacz_sie("0.0.0.0", int(self.port_podlaczenia.text()))
        
    def odswiez_ekran(self):
        if Protokol.gniazdo:
            self.label.setText(str(Protokol.nr_tury))
        if Protokol.port_nasluchu:
            self.statusBar().showMessage("Nasluchuje na porcie %s" % Protokol.port_nasluchu)