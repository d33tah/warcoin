#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys

from PyQt4 import QtGui

from Protokol import Protokol
from Okienko import Okienko

logging.getLogger('PyQt4.uic.uiparser').setLevel(logging.WARN)
logging.getLogger('PyQt4.uic.properties').setLevel(logging.WARN)
logging.getLogger().setLevel(logging.DEBUG)


if __name__=="__main__":
    Protokol.uruchom_serwer()
    app = QtGui.QApplication(sys.argv)
    t = Okienko()
    t.show()
    sys.exit(app.exec_())
    