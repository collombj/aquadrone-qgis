# coding=utf-8
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ErrorWindow:
    # Constructeur : Texte titre, texte information détaillee
    # 3eme argument : niveau de criticite ->
    # 1) information : point d'exclamation
    # 2) warning : Exclamation jaune
    # 3) critical : panneau rouge
    def __init__(self,msgText,informationText,criticalLevel):
        self.msgText = msgText
        self.informationText = informationText

        msg = QMessageBox()

        msg.setIcon(QMessageBox.Information)

        msg.setText(msgText)
        if criticalLevel == "warning":
            msg.setIcon(QMessageBox.Warning)
        elif criticalLevel == "critical":
            msg.setIcon(QMessageBox.Critical)
        elif criticalLevel == "information":
            msg.setIcon(QMessageBox.Information)
        else:
            msg.setIcon(QMessageBox.Critical)

        msg.setInformativeText(informationText)
        msg.setWindowTitle("Erreur")
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()

