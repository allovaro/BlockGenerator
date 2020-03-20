from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from mainwindow_ui import Ui_MainWindow  # импорт нашего сгенерированного файла
from application import TiaChoose        # импорт окна для выбора проекта TIA Portal
from tia_handler import TiaHandler       # импорт класса для работы с Tia Portal
import sys
import os
import logging
import configparser


class MyWindow(QtWidgets.QMainWindow):
    __processes = None
    logger = None
    tia = None
    model = None
    templates_path = None
    template_conf = None
    activate_buttons = False
    plc_name = ''

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_logger()

        self.logger.info("Program started")
        self.tia = TiaHandler()
        self.main_slots()  # Подключаем слоты
        self.settings()

        self.model = QtGui.QStandardItemModel()
        self.ui.project_tree.setModel(self.model)
        self.ui.project_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.model.setHorizontalHeaderLabels(['Дерево проекта'])
        self.ui.project_tree.setModel(self.model)

    def create_project_tree(self, children, parent):
        self.model.setHorizontalHeaderLabels(['Дерево проекта'])
        for child in children:
            child_item = QtGui.QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict):
                self.create_project_tree(children[child], child_item)

    def main_slots(self):
        self.ui.connect_action.triggered.connect(self.slot_connect_tia)
        self.ui.exit_action.triggered.connect(self.close)
        self.tia.attached_cpu.connect(self.print_cpu_tree)
        self.ui.project_tree.doubleClicked.connect(self.print_blocks_tree)
        self.ui.export_action.triggered.connect(self.export_blocks)
        self.ui.import_action.triggered.connect(self.import_blocks)
        self.ui.path_folder.triggered.connect(self.slot_folder_template)
        self.ui.sync_action.triggered.connect(self.slot_sync_action)
        self.ui.new_folder_action.triggered.connect(self.slot_new_folder)

    def slot_connect_tia(self):
        self.__processes = self.tia.get_running_instances()
        window = TiaChoose(parent=self, tia=self.__processes)
        window.return_id.connect(self.tia.attach)
        window.show()

    def slot_folder_template(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        options |= QtWidgets.QFileDialog.ShowDirsOnly
        self.templates_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выбор папки шаблонов', options=options)
        if self.templates_path:
            self.update_setting('Settings', 'template_config_path', self.templates_path)
            if not os.path.exists(self.templates_path + '/templates_params.conf'):
                self.template_conf = self.templates_path + '/templates_params.conf'
                self.create_config(self.template_conf)

    def slot_sync_action(self):
        self.update_project_tree()

    def slot_new_folder(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        QtWidgets.QInputDialog.textValueChanged.connect(test_func())
        if ok:
            print(str(text))

    def test_func(self, text):
        print(text)

    def print_cpu_tree(self, cpus):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Доступные PLC'])
        self.create_project_tree(cpus, self.model.invisibleRootItem())

    def print_blocks_tree(self, cpu):
        title = self.model.itemFromIndex(cpu).text()
        self.plc_name = title
        self.model.clear()
        self.model.setHorizontalHeaderLabels([title])
        self.tia.get_software_object(title)
        dict_str = self.tia.get_block_structure()
        self.create_program_blocks_tree(dict_str, self.model.invisibleRootItem())

    def update_project_tree(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels([self.plc_name])
        self.tia.get_software_object(self.plc_name)
        dict_str = self.tia.get_block_structure()
        self.create_program_blocks_tree(dict_str, self.model.invisibleRootItem())

    @staticmethod
    def get_children_list(parent):
        ret_list = []
        for i in range(parent.rowCount()):
            ret_list.append(parent.child(i))
        return ret_list

    @staticmethod
    def get_children_index(parent):
        ret_list = []
        for i in range(parent.rowCount()):
            ret_list.append(parent.child(i).index())
        return ret_list

    def create_tree_items_recursively(self, children, parent):
        for child in children:
            child_item = QtGui.QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict):
                self.create_project_tree(children[child], child_item)

    def add_elements_by_path(self, parent, path, elements):
        """
        Рекурсивно проходит по дереву и добавляет блоки elements по пути path
        :param parent:
        :param path:
        :param elements:
        :return:
        """
        if path:
            if parent.text() == path[0]:
                parent.appendRows(elements)
                return
            children = self.get_children_list(parent)
            for child in children:
                for path_row in path:
                    if child.text() == path_row:
                        if len(path) == 1:
                            child.appendRows(elements)
                            return
                        else:
                            self.add_elements_by_path(child, path[1:], elements)
                            return
            parent.appendRow(QtGui.QStandardItem(path[0]))
            children = self.get_children_list(parent)
            children[-1].setIcon(QtGui.QIcon('icons/folder.ico'))
            if len(path) == 1:
                children[-1].appendRows(elements)
            else:
                self.add_elements_by_path(children[-1], path[1:], elements)
        else:
            parent.appendRows(elements)

    def create_program_blocks_tree(self, dict_struct, parent):
        """
        Функция создает из словаря структуру папок и блоков
        :param dict_struct: Словарь полученный от метода tia.get_block_structure()
        :param parent: Родитель от которого начинается обход дерева
        :return:
        """
        for line in dict_struct:
            tia_blocks = []
            tia_path = self.parse_tia_folders(line)
            for i in dict_struct[line]:
                tia_blocks.append(self.set_block_icon(i))
            self.add_elements_by_path(parent, tia_path, tia_blocks)

    @staticmethod
    def set_block_icon(block):
        """
        До конца не реализованная функция по установке иконок блокам
        Щас если в конце имени содержится 'DB', то назначается иконка DB
        во всех остальных случаях FB иконка
        :param block:
        :return:
        """
        item = QtGui.QStandardItem(block)
        if block[-2:] == 'DB':
            item.setIcon(QtGui.QIcon('icons/db_block.png'))
        else:
            item.setIcon(QtGui.QIcon('icons/fb_block.png'))
        return item

    @staticmethod
    def parse_tia_folders(path):
        """
        Разделяет путь на список папок и убирает знаки '/'
        :param path: путь к папке в формате строки '/path/to/the/blocks/'
        :return: список типа ['path', 'to', 'the', 'blocks']
        """
        temp = path.split('/')
        return list(filter(None, temp))

    def export_blocks(self):
        for item in self.ui.project_tree.selectedIndexes():
            self.tia.export_block(self.model.itemFromIndex(item).text())
            print(self.model.itemFromIndex(item).text())

    def import_blocks(self):
        path_tia = None
        error = 'ERROR'
        if self.ui.project_tree.selectedIndexes():
            group_of_blocks = self.ui.project_tree.selectedIndexes()[0]
            group_of_blocks = self.model.itemFromIndex(group_of_blocks)
            if not self.tia.is_block(group_of_blocks.text()):
                path_tia = self.get_path_by_item(group_of_blocks)
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        path_to_xml, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'Выбор файлов для импорта', options=options)
        for path in path_to_xml:
            print(path_tia, path)
            path = path.replace('/', '\\')
            try:
                error = self.tia.import_block(path, path_tia)
            except:
                self.logger.info(error)
        self.update_project_tree()
        # print(path)
        # for pa in path:
        #     print(pa)
        # self.tia.import_block('Z:\\Projects\\Siemens\\BlockGenerator\\101M2_Compressor_Fan_Motor.xml', '/Мука/Силосы_металические/GBF1/')

    def get_path_by_item(self, item):
        if item.parent():
            return self.get_path_by_item(item.parent()) + item.text() + '/'
        else:
            return '/' + item.text() + '/'

    def settings(self):
        path = 'settings.conf'
        if not os.path.exists(path):
            config = configparser.ConfigParser()
            config.add_section('Settings')
            config.set('Settings', 'template_config_path', '')

            with open(path, 'w') as config_file:
                config.write(config_file)
        else:
            config = configparser.ConfigParser()
            config.read(path)
            self.templates_path = config.get('Settings', 'template_config_path')

    @staticmethod
    def get_config(path):
        """
        Returns the config object
        """
        path = 'settings.conf'
        if os.path.exists(path):
            config = configparser.ConfigParser()
            config.read(path)
            return config

    def update_setting(self, section, setting, value):
        """
        Update a setting
        """
        path = 'settings.conf'
        config = self.get_config(path)
        config.set(section, setting, value)
        with open(path, 'w') as config_file:
            config.write(config_file)

    def init_logger(self):
        """
        Initialization logger function to print information to log file
        :return:
        """
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
