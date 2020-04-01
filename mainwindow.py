from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from mainwindow_ui import Ui_MainWindow  # импорт нашего сгенерированного файла
from application import TiaChoose        # импорт окна для выбора проекта TIA Portal
from application import TemplateGen
from tia_handler import TiaHandler       # импорт класса для работы с Tia Portal
import sys
import os
import logging
import configparser
from templater import Templater


class MyWindow(QtWidgets.QMainWindow):
    __processes = None
    logger = None
    tia = None
    templater = None
    model = None
    templates_path = None
    template_conf = None
    activate_buttons = False
    prj_config = None
    prj_file_path = None
    plc_name = ''
    new_template_window = None

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_logger()
        self.init_project_table()
        self.settings()

        self.logger.info("Program started")
        self.tia = TiaHandler()
        # self.templater = Templater()
        # self.templater.new_template('Test_temp')
        self.main_slots()  # Подключаем слоты

        self.model = QtGui.QStandardItemModel()
        self.ui.project_tree.setModel(self.model)
        self.ui.project_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.model.setHorizontalHeaderLabels(['Дерево проекта'])
        self.ui.project_tree.setModel(self.model)
        self.ui.new_folder_action.setEnabled(False)
        self.ui.sync_action.setEnabled(False)
        self.ui.import_action.setEnabled(False)
        self.ui.export_action.setEnabled(False)

    def create_project_tree(self, children, parent):
        self.model.setHorizontalHeaderLabels(['Дерево проекта'])
        for child in children:
            child_item = QtGui.QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict):
                self.create_project_tree(children[child], child_item)

    def main_slots(self):
        # File Menu actions
        self.ui.open_action.triggered.connect(self.slot_open_project)
        self.ui.save_action.triggered.connect(self.save_project)
        self.ui.save_as_action.triggered.connect(self.save_project_as)
        self.ui.export_action.triggered.connect(self.export_blocks)
        self.ui.import_action.triggered.connect(self.import_blocks)
        self.ui.exit_action.triggered.connect(self.close)
        # TIA Menu actions
        self.ui.connect_action.triggered.connect(self.slot_connect_tia)
        self.ui.sync_action.triggered.connect(self.slot_sync_action)
        self.ui.new_folder_action.triggered.connect(self.slot_new_folder)
        # Template Menu actions
        self.ui.path_folder.triggered.connect(self.slot_folder_template)
        self.ui.new_row_action.triggered.connect(self.add_table_empty_line)
        self.ui.new_template_action.triggered.connect(self.slot_new_template)
        # Project Tree signals/slots
        self.tia.attached_cpu.connect(self.print_cpu_tree)
        self.ui.project_tree.doubleClicked.connect(self.print_blocks_tree)
        # MainTable widget signals/slots
        self.ui.tableWidget.cellActivated.connect(self.add_table_empty_line)

    def slot_connect_tia(self):
        self.__processes = self.tia.get_running_instances()
        window = TiaChoose(parent=self, tia=self.__processes)
        window.return_id.connect(self.tia.attach)
        window.show()

    def slot_new_template(self):
        self.window = TemplateGen()
        self.window.show()

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

    def slot_open_project(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Project file", "",
                                                             "Project Files (*.prj);;All Files (*)", options=options)
        if fileName:
            self.prj_file_path = fileName
            self.prj_config = self.get_config(fileName)
            for section in self.prj_config.sections():
                if section == 'zones':
                    pass
                elif section == 'settings':
                    pass
                else:
                    self.add_project_line(self.prj_config, section)

    def slot_sync_action(self):
        self.update_project_tree()

    def slot_new_folder(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        # QtWidgets.QInputDialog.textValueChanged.connect(test_func())
        if ok:
            self.tia.create_group(text)
            self.update_project_tree()

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
        self.ui.new_folder_action.setEnabled(True)
        self.ui.sync_action.setEnabled(True)
        self.ui.import_action.setEnabled(True)
        self.ui.export_action.setEnabled(True)

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

    def init_project_table(self):
        self.ui.tableWidget.setColumnCount(18)  # Устанавливаем три колонки
        self.ui.tableWidget.setRowCount(0)  # и одну строку в таблице
        # Устанавливаем заголовки таблицы
        self.ui.tableWidget.setHorizontalHeaderLabels(['Название блока', 'Шаблон', 'Имя элемента', 'Номер',
                                                       'Сброс', 'Безопасность', 'Режим авто', 'Путь', 'Блок вызова',
                                                       'Клапан NO/NC', 'Теги', 'Дат. давл. аналог.', 'Дат. давл. дискр',
                                                       'SEQ_Pause', 'SEQ_in_Progress', 'Клапан вибросита',
                                                       'Триг. фильтров', 'Симулятор'])
        self.ui.tableWidget.resizeColumnsToContents()

    def add_table_empty_line(self):
        self.ui.tableWidget.setRowCount(self.ui.tableWidget.rowCount() + 1)
        combo_templ = QtWidgets.QComboBox()
        combo_templ.addItems(self.get_templates_list())
        combo_tags = QtWidgets.QComboBox()
        combo_tags.addItems(['', 'AUX', 'IO', 'AUX+IO'])
        for column in range(self.ui.tableWidget.columnCount()):
            self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount() - 1, column, QtWidgets.QTableWidgetItem(''))
        self.ui.tableWidget.setCellWidget(self.ui.tableWidget.rowCount() - 1, 1, combo_templ)
        self.ui.tableWidget.setCellWidget(self.ui.tableWidget.rowCount() - 1, 10, combo_tags)

    def copy_table_line(self, line_num):
        row_num = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.setRowCount(row_num + 1)
        combo_templ = QtWidgets.QComboBox()
        combo_templ.addItems(self.get_templates_list())
        self.ui.tableWidget.setCellWidget(row_num, 1, combo_templ)
        self.ui.tableWidget.setItem(row_num, 0, QtWidgets.QTableWidgetItem("Texfffff"))
        self.ui.tableWidget.resizeColumnsToContents()

    def get_row_table(self, row):
        ret = []
        for i in range(self.ui.tableWidget.columnCount()):
            print(i)
            if i == 1:
                ret.append(self.get_templ_from_table(row))
            elif i == 10:
                ret.append(self.get_tags_from_table(row))
            else:
                ret.append(self.ui.tableWidget.item(row, i).text())
        return ret

    def get_templ_from_table(self, row):
        return self.ui.tableWidget.cellWidget(row, 1).currentText()

    def get_tags_from_table(self, row):
        return self.ui.tableWidget.cellWidget(row, 10).currentText()

    def add_project_line(self, project, section):
        row_num = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.setRowCount(row_num + 1)
        combo_templ = QtWidgets.QComboBox()
        combo_templ.addItems(self.get_templates_list())
        combo_tags = QtWidgets.QComboBox()
        combo_tags.addItems(['', 'AUX', 'IO', 'AUX+IO'])
        counter = 1
        self.ui.tableWidget.setItem(row_num, 0, QtWidgets.QTableWidgetItem(section))
        for option in project.options(section):
            value = project.get(section, option)
            if option == 'шаблон':
                self.ui.tableWidget.setCellWidget(row_num, 1, combo_templ)
                self.ui.tableWidget.cellWidget(row_num, 1).setCurrentText(value)
            elif option == 'теги':
                self.ui.tableWidget.setCellWidget(row_num, 10, combo_tags)
                self.ui.tableWidget.cellWidget(row_num, 10).setCurrentText(value)
            else:
                self.ui.tableWidget.setItem(row_num, counter, QtWidgets.QTableWidgetItem(value))
            counter += 1
        self.ui.tableWidget.resizeColumnsToContents()

    def save_project(self):
        new_config = configparser.ConfigParser()
        for row in range(self.ui.tableWidget.rowCount()):
            new_config.add_section(self.ui.tableWidget.item(row, 0).text())
            for column in range(1, self.ui.tableWidget.columnCount()):
                if column == 1 or column == 10:
                    new_config.set(self.ui.tableWidget.item(row, 0).text(),
                                   self.ui.tableWidget.horizontalHeaderItem(column).text(),
                                   self.ui.tableWidget.cellWidget(row, column).currentText())
                else:
                    new_config.set(self.ui.tableWidget.item(row, 0).text(),
                                   self.ui.tableWidget.horizontalHeaderItem(column).text(),
                                   self.ui.tableWidget.item(row, column).text())
        with open(self.prj_file_path, 'w') as config_file:
            new_config.write(config_file)

    def save_project_as(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog # Qt's builtin File Dialogue
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Open", "", "All Files (*.prj)", options=options)
        if fileName:
            print(fileName[-4:])
            if fileName[-4:] == '.prj':
                self.prj_file_path = fileName
            else:
                self.prj_file_path = fileName + '.prj'
            print(self.prj_file_path)
            self.save_project()

    @staticmethod
    def get_templates_list():
        # Каталог из которого будем брать шаблоны
        directory = 'templates'
        # Получаем список файлов в переменную files
        files = os.listdir(directory)
        # Фильтруем список
        templ = list(filter(lambda x: x.endswith('.tpl'), files))
        ret = []
        for item in templ:
            ret.append(item[:-4])
        return ret

    @staticmethod
    def get_config(path):
        """
        Returns the config object
        """
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
