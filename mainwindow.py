from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from mainwindow_ui import Ui_MainWindow  # импорт нашего сгенерированного файла
from tia_proc_ui import Ui_tia_chooser   # импорт сгенерированного файла для выбора процесса TIA
from application import TiaChoose        # импорт окна для выбора проекта TIA Portal
from tia_handler import TiaHandler       # импорт класса для работы с Tia Portal
import sys, logging, configparser


class MyWindow(QtWidgets.QMainWindow):
    __processes = None
    logger = None
    tia = None
    model = None
    root = None

    tree = {
        'parent 1': ["child 1-1"],
        'child 1-2': [],
        'child 1-3': ["child 1-1-1"],
        'children 2-1': ["..."],
        "parent 2": ["..."],
        "parent 3": [],
        "parent 4": [],
        "par 5": {"one": ["two", "three"]}
    }

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_logger()

        self.logger.info("Program started")
        self.tia = TiaHandler()
        self.main_slots()  # Подключаем слоты

        model = QtGui.QStandardItemModel()
        self.ui.project_tree.setModel(model)
        self.create_project_tree(self.tree, model.invisibleRootItem())
        self.ui.project_tree.setModel(model)
        model.setHeaderData(0, QtCore.Qt.Horizontal, 'PLC')

        # self.ui.projectView.setRootIsDecorated(False)
        # self.ui.projectView.setAlternatingRowColors(True)
        # self.model = self.create_project_model(self)
        # self.ui.projectView.setModel(self.model)
        # self.root = self.model.invisibleRootItem()

        # self.root.appendRow(QtGui.QStandardItem('Test string'))
        # root.appendRow(QtGui.QStandardItem('Test string234'))
        # root.child(root.rowCount() - 1)
        # root.appendRow(QtGui.QStandardItem('Test string1'))
        # print(root[0])

    def create_project_tree(self, children, parent):
        for child in children:
            child_item = QtGui.QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict):
                self.create_project_tree(children[child], child_item)

    @staticmethod
    def create_project_model(parent):
        model = QtGui.QStandardItemModel(0, 3, parent)
        model.setHorizontalHeaderLabels(['Название', 'Тип', 'Номер'])
        # model.
        return model

    def main_slots(self):
        self.ui.connect_action.triggered.connect(self.slot_connect_tia)
        self.ui.exit_action.triggered.connect(self.close)
        self.tia.attached_cpu.connect(self.print_cpu_tree)

    def slot_connect_tia(self):
        self.__processes = self.tia.get_running_instances()
        window = TiaChoose(parent=self, tia=self.__processes)
        window.return_id.connect(self.tia.attach)
        window.show()

    def print_cpu_tree(self, cpus):
        self.root.clear()
        for cpu in cpus:
            self.root.appendRow(QtGui.QStandardItem(str(cpu)))
    # def print_hello(self, path):
    #     self.tia.attach(path)

    def init_logger(self):
        self.logger = logging.getLogger("MyWindow")
        self.logger.setLevel(logging.INFO)

        # create the logging file handler
        fh = logging.FileHandler("logs.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        self.logger.addHandler(fh)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    application = MyWindow()  # Создаём объект класса MyWindow
    application.show()  # Показываем окно
    sys.exit(app.exec())  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
