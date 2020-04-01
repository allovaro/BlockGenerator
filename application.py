from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5 import QtGui
from PyQt5.QtCore import (Qt, pyqtSignal)
from tia_proc_ui import Ui_tia_chooser    # импорт сгенерированного файла для выбора процесса TIA
from templater_ui import Ui_Template_Gen
import logging


class TiaChoose(QMainWindow, Ui_tia_chooser):
    logger = None
    return_id = pyqtSignal(str)

    def __init__(self, parent=None, tia=None):
        super(TiaChoose, self).__init__(parent)
        self.setupUi(self)
        self.init_logger()

        buttons = []
        coor = 5
        self.logger.info('window opened')
        if tia:
            counter = 1
            for item in tia:
                path = str(item.ProjectPath).split('\\')
                buttons.append(QPushButton(str(counter) + '. ' + path[-1], self))
                buttons[-1].setMinimumWidth(300)
                buttons[-1].move(5, coor)
                buttons[-1].setShortcut(str(counter))
                buttons[-1].setToolTip(str(item.ProjectPath))
                buttons[-1].clicked.connect(self.emit_signal)
                coor += 30
                counter += 1
        self.setGeometry(300, 300, 310, coor + 5)

    def emit_signal(self):
        self.return_id.emit(self.sender().toolTip())
        self.logger.info(self.sender().toolTip())
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def init_logger(self):
        self.logger = logging.getLogger("TiaChooser")
        self.logger.setLevel(logging.INFO)

        # create the logging file handler
        fh = logging.FileHandler("logs.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        self.logger.addHandler(fh)


class TemplateGen(QMainWindow, Ui_Template_Gen):

    def __init__(self, parent=None):
        super(TemplateGen, self).__init__(parent)
        self.setupUi(self)
        # hbox = QHBoxLayout()
        # hbox.addWidget(self.ui.verticalLayout_2)
        # hbox.addWidget(self.ui.verticalLayout_3)
        # self.setLayout(hbox)
