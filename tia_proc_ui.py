# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tia_proc.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_tia_chooser(object):
    def setupUi(self, tia_chooser):
        tia_chooser.setObjectName("tia_chooser")
        tia_chooser.resize(306, 176)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/3d.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        tia_chooser.setWindowIcon(icon)

        self.retranslateUi(tia_chooser)
        QtCore.QMetaObject.connectSlotsByName(tia_chooser)

    def retranslateUi(self, tia_chooser):
        _translate = QtCore.QCoreApplication.translate
        tia_chooser.setWindowTitle(_translate("tia_chooser", "Открытые проекты"))

