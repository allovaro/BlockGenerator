import clr
import logging
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V14\PublicAPI\\V14 SP1\\Siemens.Engineering.dll')
import Siemens.Engineering as tia
import Siemens.Engineering.HW.Features as hwf
from System.IO import DirectoryInfo, FileInfo
from PyQt5.QtCore import (QObject, pyqtSignal)


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

    def __init__(self, parent=None):
        super(TiaHandler, self).__init__(parent)
        self.init_logger()
        pass

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
    # Методы для работы с блоками
    # --------------------------------------------------------

    @staticmethod
    def get_all_blocks(sf_container):
        grp = sf_container.Software.BlockGroup.Groups.Find('OB_FLT')
        # print(len(grp.Groups))

        # for item in sf_container.Software.BlockGroup.Groups:
        #     print(item.Groups)
        #     print(item.Name)
            # for itm in item.Groups:
            #     print(itm.Name)
            #     for itm1 in itm.Groups:
            #         print(itm1.Name)

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

    @staticmethod
    def import_block_xml(path_to_file, block_group):
        return block_group.Blocks.Import(FileInfo(path_to_file), tia.ImportOptions.Override)

# processes = self.get_running_instances()
# mytia = processes[1].Attach()
# my_project = mytia.Projects[0]  # Подключаемся к первому проекту в этом экземпляре TIA
# for device in my_project.Devices:
#     device_item_aggregation = device.DeviceItems
#     print('----------')
#     print(device.Name)
#     for deviceitem in device_item_aggregation:
#             software_container = tia.IEngineeringServiceProvider(deviceitem).GetService[hwf.SoftwareContainer]()
#             if (software_container):
#                 print(f'Device name: {deviceitem.Name}')
#                 software_base = software_container.Software
#--------------------------------------------------------------------------------------------------
            # Starting TIA
            # print ('Connecting TIA')
            # item = tia.TiaPortal.GetProcesses()  # Смотрим запущенные процессы TIA
            # print(item[1].ProjectPath)  # Выводим путь открытого проекта
            # mytia = item[1].Attach()  # Подключаемся к первому экземпляру
            # my_project = mytia.Projects[0]  # Подключаемся к первому проекту в этом экземпляре TIA
            # software_container = tia.IEngineeringServiceProvider(PLC1.DeviceItems[1]).GetService[hwf.SoftwareContainer]()
            # for device in my_project.Devices:
            #     device_item_aggregation = device.DeviceItems
            #     print(device)

            # print(my_project.Devices[0].DeviceItems[1])
# software_container = tia.IEngineeringServiceProvider(my_project.Devices[0].DeviceItems[0]).GetService[hwf.SoftwareContainer]()
# software_container = tia.IEngineeringServiceProvider(my_project.Devices[0].DeviceItems[0]).GetService[hwf.SoftwareContainer]()
# print(software_container)
# print(my_project.Devices.Find('CEPI_317PN/DP'))
# print(my_project.Devices[1].GetAttribute('TypeName'))
# for item in my_project.Devices:
#     print(item.GetAttribute('TypeName'))
# print(my_project.Devices[0].DeviceItems[0].GetService())

# mytia = tia.TiaPortal(tia.TiaPortalMode.WithUserInterface)

# #Creating new project
# print ('Creating project')
# myproject = mytia.Projects.Create(project_path, project_name)
#
# #Addding Stations
# print ('Creating station 1')
# station1_mlfb = 'OrderNumber:6ES7 515-2AM01-0AB0/V2.6'
# station1 = myproject.Devices.CreateWithItem(station1_mlfb, 'station1', 'station1')
#
# print ('Creating station 2')
# station2_mlfb = 'OrderNumber:6ES7 518-4AP00-0AB0/V2.6'
# station2 = myproject.Devices.CreateWithItem(station2_mlfb, 'station2', 'station2')