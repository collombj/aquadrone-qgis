import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ErrorWindow:

    def __init__(self,msgText,informationText,):
        self.msgText = msgText
        self.informationText = informationText

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText(msgText)
        msg.setIcon(QMessageBox.Warning)

        msg.setInformativeText(informationText)
        msg.setWindowTitle("Erreur")
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()
        return 0
