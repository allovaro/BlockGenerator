import clr
import logging
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V14\\PublicAPI\\V14 SP1\\Siemens.Engineering.dll')
import Siemens.Engineering as tia
import Siemens.Engineering.HW.Features as hwf
from System.IO import DirectoryInfo, FileInfo
import os
from PyQt5.QtCore import (QObject, pyqtSignal)
from lxml import etree, objectify
import re
import templater


class TiaHandler(QObject):
    __processes = None
    __connection = False
    logger = None
    tia_obj = None
    prj_obj = None
    attached_cpu = pyqtSignal(dict)
    cpu = []
    software_container = None
    folders = []
    ExportPath = 'templates/xml/'

    def __init__(self, parent=None):
        super(TiaHandler, self).__init__(parent)
        self.init_logger()
        # self.compressor_cmd('57M_Compressor', '7898', 'No', 'No', '57M',
        #                     'Powder_B2_Load_Auto_Mode', 'Reset_Err_Silos_Area', 'Системы_шкаф_Q1_Готовы', 'FaultName.Melnica')

    def get_running_instances(self):
        self.__processes = tia.TiaPortal.GetProcesses()
        return self.__processes

    def attach(self, path):
        for item in self.__processes:
            if str(item.ProjectPath) == path:
                self.tia_obj = item.Attach()
                if self.tia_obj:
                    self.__connection = True
                    self.logger.info('Connected to ' + str(item.ProjectPath))
                else:
                    self.__connection = False
                self.prj_obj = self.tia_obj.Projects[0]
                # self.cpu = self.get_cpu_list()
                # self.get_software_object()
                self.attached_cpu.emit(self.get_cpu_list())
                return True
        return False

    def is_connected(self):
        if self.__connection:
            return True
        else:
            return False

    def is_plc(self):
        if self.software_container:
            return True
        else:
            return False

    def init_logger(self):
        """
        Initialization logger function to print information to log file
        :return:
        """
        self.logger = logging.getLogger("TiaHandler")
        self.logger.setLevel(logging.INFO)

        # create the logging file handler
        fh = logging.FileHandler("logs.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        self.logger.addHandler(fh)

    def get_cpu_list(self):
        cpu = []
        for device in self.prj_obj.Devices:
            device_item_aggregation = device.DeviceItems
            for item in device_item_aggregation:
                if item.Classification == tia.HW.DeviceItemClassifications.CPU:
                    cpu.append(item.Name)
        if cpu:
            empty_list = []
            return dict.fromkeys(cpu, empty_list)
        return None

    def get_software_object(self, cpu_name):
        """
        Записывает в переменную self.software_container объект TIA портала для
        дальшей работы с блоками, папками, тегами и так далее
        :return:
        """
        for device in self.prj_obj.Devices:
            device_item_aggregation = device.DeviceItems
            for device_item in device_item_aggregation:
                if device_item.Name == cpu_name and device_item.Classification == tia.HW.DeviceItemClassifications.CPU:
                    self.software_container = tia.IEngineeringServiceProvider(device_item).GetService[
                        hwf.SoftwareContainer]()

                    # software_container.Software.BlockGroup.Blocks.Import(FileInfo('Z:\\Projects\\Siemens\\BlockGenerator\\valve_no.xml'), tia.ImportOptions.Override)
                    # self.get_blocks(software_container)
                    # dict1 = self.get_folders()
                    # print(dict1.get('/Мука/Силосы_тряпичные/STL2/'))

                    # self.get_folders_recursively(self.software_container.Software.BlockGroup, '/')
                    # table = self.create_tag_table(software_container, 'wqe')
                    # table.Tags.Create('new_tag', 'Bool', '')
                    # table1 = self.find_tag_table(software_container, 'Aux1')
                    # print(table1)
                    # tags = self.get_tags(table1)
                    # for tag in tags:
                    #     print(tag)
    # --------------------------------------------------------
    # Методы для работы с таблицами символов
    # --------------------------------------------------------
    @staticmethod
    def create_tag_table(sf_container, name):
        """
        Создает таблицу символов
        :param sf_container: Ожидает Siemens.Engineering.HW.Features.SoftwareContainer
        :param name: Название символьной таблицы в типе str
        :return: Если успех возвращает Siemens.Engineering.SW.Tags.PlcTagTable, во всех остальных случаях False
        """
        if isinstance(name, str):
            if sf_container:
                software_base = sf_container.Software
                tag_table_group = software_base.TagTableGroup
                return tag_table_group.TagTables.Create(name)
        return False

    @staticmethod
    def find_tag_table(sf_container, name):
        """
        Найти таблицу символов по имени
        :param sf_container: Ожидает Siemens.Engineering.HW.Features.SoftwareContainer
        :param name: Название символьной таблицы в типе str
        :return: Если Ок, возвращает Siemens.Engineering.SW.Tags.PlcTagTable, во всех остальных случаях None
        """
        if isinstance(name, str):
            return sf_container.Software.TagTableGroup.TagTables.Find(name)
        return None

    @staticmethod
    def get_tags(tag_table):
        if type(tag_table) == tia.SW.Tags.PlcTagTable:
            tags = []
            for tag in tag_table.Tags:
                tags.append([tag.Name, tag.DataTypeName, tag.LogicalAddress])
            return tags
        return False

    # --------------------------------------------------------
    # Методы для работы с блоками и папками
    # --------------------------------------------------------
    def get_blocks_recursively(self, block_group):
        """
        Получить названия всех блоков одним списком
        :param block_group:
        :return:
        """
        temp = []
        for item in block_group.Blocks:
            temp.append(item.Name)
        for item in block_group.Groups:
            temp = temp + self.get_blocks_recursively(item)
        return temp

    def get_block_by_name(self, block_group, name):
        """
        По названию блока возвращает объект
        :param block_group:
        :param name:
        :return:
        """
        for item in block_group.Blocks:
            if item.Name == name:
                return item
        for item in block_group.Groups:
            block = self.get_block_by_name(item, name)
            if block:
                return block

    def is_block(self, name):
        """
        Проверка по названию блок или папка
        :param name:
        :return: Если блок возвращает True
        """
        block_list = self.get_blocks_recursively(self.software_container.Software.BlockGroup)
        for block in block_list:
            if block == name:
                return True
        return False

    def get_block_structure(self):
        my_dict = dict()
        self.folders = []
        self.get_folders_recursively(self.software_container.Software.BlockGroup, '/')
        for line in self.folders:
            key = line.pop(0)
            my_dict[key] = line
        return my_dict

    def get_folders_recursively(self, block_group, lvl):
        temp = [lvl]
        for item in block_group.Blocks:
            temp.append(item.Name)
        self.folders.append(temp)
        for item in block_group.Groups:
            self.get_folders_recursively(item, lvl + item.Name + '/')

    def get_block_group(self, block_group, path):
        group = None
        if not path:
            return block_group
        for path_line in path:
            group = block_group.Find(path_line)
            if group:
                print(group.Name)
                if len(path) == 1:
                    return group
                return self.get_block_group(group.Groups, path[1:])
        return block_group

    def create_group(self, path):
        path_list = list(filter(None, path.split('/')))
        if len(path_list) > 1:
            print(path_list)
            block_group = self.get_block_group(self.software_container.Software.BlockGroup.Groups, path_list)
            block_group.Create(path_list[-1])
        else:
            if path_list:
                self.software_container.Software.BlockGroup.Groups.Create(path_list[0])

    def import_block(self, path_to_file, path_tia):
        print(path_tia)
        if os.path.exists(path_to_file):
            if path_tia:
                path_list = list(filter(None, path_tia.split('/')))
                block_group = self.get_block_group(self.software_container.Software.BlockGroup.Groups, path_list)
                return block_group.Blocks.Import(FileInfo(path_to_file), tia.ImportOptions.Override)
            else:
                return self.software_container.Software.BlockGroup.Blocks.Import(FileInfo(path_to_file),
                                                                                 tia.ImportOptions.Override)
        else:
            return 'path to imported file does not exist'

    def export_block(self, name):
        block_group = self.software_container.Software.BlockGroup
        block = self.get_block_by_name(block_group, name)
        if block:
            self.logger.info('Block ' + name + ' was exported')
            block.Export(FileInfo('Z:\\Projects\\Siemens\\BlockGenerator\\export\\' + name + '.xml'),
                         tia.ExportOptions.WithDefaults)
        else:
            self.logger.error('Block ' + name + ' was not found')

    # --------------------------------------------------------
    # Методы для подготовки xml файла для импорта в TIA
    # --------------------------------------------------------
    def generate_block(self, template_name):
        template_config = Templater()
        template_config.get_config(template_name)

    def compressor_cmd(self, name, num, ps, psa, m, autoname, rstname, alarmname, faultname):
        # Пути для исходного xml файла и конечного
        path_to_source = self.ExportPath + 'compressor.xml'
        path_to_dest = self.ExportPath + 'tmp/' + name + '.xml'

        # Удаление из xml строк которые мешают его обработке библиотекой lxml
        self.preparing_xml(path_to_source, name)

        # Замена названий блока, переменных и коментариев
        self.set_block_name(path_to_dest, name, num)
        self.change_glob_var_names(path_to_dest, 'Glob_rst', rstname)
        self.change_glob_var_names(path_to_dest, 'Glob_Mode', autoname)
        self.change_glob_var_names(path_to_dest, 'Системы_шкаф_Q4_Готовы', alarmname)
        # Поиск бита аварии в Faults блоке данных
        if os.path.isfile(self.ExportPath + 'Faults.xml') and ps != 'No':
            path1, path2 = find_elem_by_name(self.ExportPath + 'Faults.xml', ps)
            self.change_glob_var_names(path_to_dest, 'Fault_name_2', path2)
        self.change_glob_var_names(path_to_dest, 'Fault_struct', faultname.split('.')[0])
        self.change_glob_var_names(path_to_dest, 'Fault_name', faultname.split('.')[1])
        self.change_var_names(path_to_dest, '408', m[:-1])
        self.change_glob_var_names(path_to_dest, '408', m[:-1])

        # Добавление нетворка обработки дискретного датчика давления
        if ps != 'No' or '':
            self.change_glob_var_names(path_to_dest, '498VS', ps)
        else:
            self.delete_network(path_to_dest, '17')
            self.delete_network(path_to_dest, '20')
            self.delete_network(path_to_dest, '29')
            self.delete_network(path_to_dest, '32')
            self.delete_network(path_to_dest, '3B')

        # Добавление нетворка обработки аналогого датчика давления
        if psa != 'No' or '':
            self.change_glob_var_names(path_to_dest, '499VS', psa)
        else:
            self.delete_network(path_to_dest, '7A')

        # возврат удаленных строк в конечный xml файл
        self.return_xml_to_initial(name)

    def inverter_cmd(self, name, num, m, autoname, rstname, alarmname, faultname):
        if not name:
            name = 'New_inverter'
        if not num:
            num = '9999'
        if not m:
            m = '999UF'
        if not autoname:
            autoname = 'AutoMan'
        if not rstname:
            rstname = 'Reset_Err_'
        if not alarmname:
            alarmname = 'General_Alarm'
        # Пути для исходного xml файла и конечного
        self.path_to_source = self.ExportPath + 'inverter.xml'
        self.path_to_dest = self.ExportPath + name + '.xml'

        # Удаление из xml строк которые мешают его обработке библиотекой lxml
        self.preparing_xml(path_to_source, name)

        # Замена названий блока, переменных и коментариев
        self.set_block_name(path_to_dest, name, num)
        self.change_glob_var_names(path_to_dest, 'Glob_rst', rstname)
        self.change_glob_var_names(path_to_dest, 'Glob_Mode', autoname)
        self.change_glob_var_names(path_to_dest, 'Системы_шкаф_Q4_Готовы', alarmname)
        self.change_glob_var_names(path_to_dest, 'Fault_struct', faultname.split('.')[0])
        self.change_glob_var_names(path_to_dest, 'Fault_name', faultname.split('.')[1])
        self.change_var_names(path_to_dest, '453', m[:-2])
        self.change_glob_var_names(path_to_dest, '453', m[:-2])

        # возврат удаленных строк в конечный xml файл
        self.return_xml_to_initial(name)

    def preparing_xml(self, xmlFile, name):
        """
        Удаляет строку со ссылкой, которая не нравится lxml и копирует
        в новый файл
        :param xmlFile: Исходный файл образец компрессора
        :param name: Имя блока на основе которого будет создан новый файл
        :return: None
        """
        f = open(xmlFile, 'r', encoding="utf-8")
        lines = f.readlines()
        f.close()
        f = open(self.ExportPath + 'tmp/' + name + '.xml', 'w', encoding="utf-8")
        for line in lines:
            if line.find(
                    '<NetworkSource><FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v1">') != -1:
                f.write('          <NetworkSource><FlgNet>\n')
            elif line.find(
                    '<Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v2">') != -1:
                f.write('    <Interface><Sections>' + '\n')
            else:
                f.write(line)
        f.close()

    def return_xml_to_initial(self, name):
        """
        Возврат удаленной ссылки функцией preparing_xml() на первоначальное место
        :param name: Название xml файла
        :return: None
        """
        f = open(self.ExportPath + 'tmp/' + name + '.xml', 'r', encoding="utf-8")
        lines = f.readlines()
        f.close()
        f = open(self.ExportPath + 'tmp/' + name + '.xml', 'w', encoding="utf-8")
        for line in lines:
            if line.find('    <Interface><Sections>') != -1:
                f.write(
                    '    <Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v2">' + '\n')
            elif line.find('          <NetworkSource><FlgNet>') != -1:
                f.write(
                    '<NetworkSource><FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v1">\n')
            else:
                f.write(line)
        f.close()

    def set_block_name(self, xmlFile, name, num):
        """
        Изменение названия и номера нового блока
        :param xmlFile: Путь к файлу
        :param name: Новой имя блока
        :param num: Новый номер блока
        :return: None
        """
        tree = etree.parse(xmlFile)
        block_name = tree.xpath('/Document/SW.Blocks.FB/AttributeList/Name')
        block_num = tree.xpath('/Document/SW.Blocks.FB/AttributeList/Number')
        block_name[0].text = name
        block_num[0].text = num
        tree.write(xmlFile, encoding="utf-8")

    def delete_network(self, xmlFile, network_id):
        tree = etree.parse(xmlFile)
        path_to_network = '//SW.Blocks.CompileUnit[@ID=' + "'" + str(network_id) + "']"
        #    path = tree.xpath('/Document/SW.Blocks.FB/ObjectList/SW.Blocks.CompileUnit')
        path = tree.xpath(path_to_network)
        path[0].getparent().remove(path[0])
        tree.write(xmlFile, encoding="utf-8")

    def change_glob_var_names(self, path_to_file, old_name, new_name):
        """
        Изменяет глобальные названия тегов в нетворках
        """
        tree = etree.parse(path_to_file)

        glob_variables = tree.xpath(
            '/Document/SW.Blocks.FB/ObjectList/SW.Blocks.CompileUnit/AttributeList/NetworkSource/FlgNet/Parts/Access/Symbol/Component')  # Путь к именам переменных

        for node in glob_variables:  # Перебираем элементы
            # print(node.tag)
            if node.get('Name').find(old_name) != -1:
                node.set('Name', node.get('Name').replace(old_name, new_name))
            # print('name =', node.get('Name'))  # Выводим параметр name
            # print(node.text)  # Выводим текст элемента

        tree.write(path_to_file, encoding="utf-8")

    def change_var_names(self, path_to_file, old_name, new_name):
        tree = etree.parse(path_to_file)

        hmi_variables = tree.xpath(
            '/Document/SW.Blocks.FB/AttributeList/Interface/Sections/Section/Member')  # Путь к именам переменных
        block_variables = tree.xpath(
            '/Document/SW.Blocks.FB/AttributeList/Interface/Sections/Section/Member/Member/Member')  # Путь к именам переменных

        for node in block_variables:  # Перебираем элементы
            # print(node.tag)
            if node.get('Name').find(old_name) != -1:
                node.set('Name', node.get('Name').replace(old_name, new_name))
            # print('name =', node.get('Name'))  # Выводим параметр name
            # print(node.text)  # Выводим текст элемента

        for node in hmi_variables:  # Перебираем элементы
            # print(node.tag)
            if node.get('Name').find(old_name) != -1:
                node.set('Name', node.get('Name').replace(old_name, new_name))
            # print('name =', node.get('Name'))  # Выводим параметр name
            # print(node.text)  # Выводим текст элемента
        tree.write(path_to_file, encoding="utf-8")