# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1281, 739)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/3d.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(271, 16777215))
        self.tabWidget.setObjectName("tabWidget")
        self.project_tab = QtWidgets.QWidget()
        self.project_tab.setObjectName("project_tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.project_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.project_tree = QtWidgets.QTreeView(self.project_tab)
        self.project_tree.setObjectName("project_tree")
        self.verticalLayout.addWidget(self.project_tree)
        self.tabWidget.addTab(self.project_tab, "")
        self.template_tab = QtWidgets.QWidget()
        self.template_tab.setObjectName("template_tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.template_tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.template_list = QtWidgets.QListView(self.template_tab)
        self.template_list.setObjectName("template_list")
        self.gridLayout_2.addWidget(self.template_list, 0, 0, 1, 1)
        self.tabWidget.addTab(self.template_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1281, 21))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_project = QtWidgets.QMenu(self.menubar)
        self.menu_project.setObjectName("menu_project")
        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.menu_help.setObjectName("menu_help")
        self.menu_template = QtWidgets.QMenu(self.menubar)
        self.menu_template.setObjectName("menu_template")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.connect_action = QtWidgets.QAction(MainWindow)
        self.connect_action.setEnabled(True)
        self.connect_action.setIconVisibleInMenu(True)
        self.connect_action.setShortcutVisibleInContextMenu(True)
        self.connect_action.setObjectName("connect_action")
        self.open_action = QtWidgets.QAction(MainWindow)
        self.open_action.setObjectName("open_action")
        self.save_action = QtWidgets.QAction(MainWindow)
        self.save_action.setObjectName("save_action")
        self.save_as_action = QtWidgets.QAction(MainWindow)
        self.save_as_action.setObjectName("save_as_action")
        self.sync_action = QtWidgets.QAction(MainWindow)
        self.sync_action.setEnabled(True)
        self.sync_action.setObjectName("sync_action")
        self.exit_action = QtWidgets.QAction(MainWindow)
        self.exit_action.setObjectName("exit_action")
        self.path_folder = QtWidgets.QAction(MainWindow)
        self.path_folder.setObjectName("path_folder")
        self.export_action = QtWidgets.QAction(MainWindow)
        self.export_action.setObjectName("export_action")
        self.import_action = QtWidgets.QAction(MainWindow)
        self.import_action.setObjectName("import_action")
        self.new_folder_action = QtWidgets.QAction(MainWindow)
        self.new_folder_action.setCheckable(False)
        self.new_folder_action.setChecked(False)
        self.new_folder_action.setEnabled(True)
        self.new_folder_action.setAutoRepeat(True)
        self.new_folder_action.setVisible(True)
        self.new_folder_action.setIconVisibleInMenu(True)
        self.new_folder_action.setObjectName("new_folder_action")
        self.new_template_action = QtWidgets.QAction(MainWindow)
        self.new_template_action.setObjectName("new_template_action")
        self.from_template_action = QtWidgets.QAction(MainWindow)
        self.from_template_action.setObjectName("from_template_action")
        self.new_row_action = QtWidgets.QAction(MainWindow)
        self.new_row_action.setObjectName("new_row_action")
        self.menu_file.addAction(self.open_action)
        self.menu_file.addAction(self.save_action)
        self.menu_file.addAction(self.save_as_action)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.export_action)
        self.menu_file.addAction(self.import_action)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.exit_action)
        self.menu_project.addAction(self.connect_action)
        self.menu_project.addAction(self.sync_action)
        self.menu_project.addAction(self.new_folder_action)
        self.menu_template.addAction(self.path_folder)
        self.menu_template.addAction(self.new_template_action)
        self.menu_template.addAction(self.from_template_action)
        self.menu_template.addAction(self.new_row_action)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_project.menuAction())
        self.menubar.addAction(self.menu_template.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Block Generator"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.project_tab), _translate("MainWindow", "Проект"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.template_tab), _translate("MainWindow", "Шаблоны"))
        self.menu_file.setTitle(_translate("MainWindow", "Файл"))
        self.menu_project.setTitle(_translate("MainWindow", "TIA"))
        self.menu_help.setTitle(_translate("MainWindow", "Помощь"))
        self.menu_template.setTitle(_translate("MainWindow", "Шаблоны"))
        self.connect_action.setText(_translate("MainWindow", "Подлючиться к проекту"))
        self.connect_action.setShortcut(_translate("MainWindow", "Ctrl+Shift+O"))
        self.open_action.setText(_translate("MainWindow", "Открыть"))
        self.open_action.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.save_action.setText(_translate("MainWindow", "Сохранить"))
        self.save_action.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.save_as_action.setText(_translate("MainWindow", "Сохранить Как ..."))
        self.save_as_action.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.sync_action.setText(_translate("MainWindow", "Синхронизировать"))
        self.exit_action.setText(_translate("MainWindow", "Выход"))
        self.exit_action.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.path_folder.setText(_translate("MainWindow", "Путь к файлам"))
        self.export_action.setText(_translate("MainWindow", "Экспорт"))
        self.export_action.setShortcut(_translate("MainWindow", "Ctrl+E"))
        self.import_action.setText(_translate("MainWindow", "Импорт"))
        self.import_action.setShortcut(_translate("MainWindow", "Ctrl+I"))
        self.new_folder_action.setText(_translate("MainWindow", "Новая папка"))
        self.new_template_action.setText(_translate("MainWindow", "Новый шаблон"))
        self.from_template_action.setText(_translate("MainWindow", "Создать из шаблона"))
        self.new_row_action.setText(_translate("MainWindow", "Новая строка"))

