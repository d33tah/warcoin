#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys

from PyQt4 import QtGui

from Polaczenie import Polaczenie
from Okienko import Okienko

logging.getLogger('PyQt4.uic.uiparser').setLevel(logging.WARN)
logging.getLogger('PyQt4.uic.properties').setLevel(logging.WARN)
logging.getLogger().setLevel(logging.DEBUG)


if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    Polaczenie.uruchom_serwer()
    Okienko.instance().show()
    sys.exit(app.exec_())
    