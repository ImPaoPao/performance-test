# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import collections
import copy
import os
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import runner
from common import workdir
from tools import get_prop

import subprocess

import module


class BuildSetupWizard(QWizard):
    def __init__(self, parent):
        super(BuildSetupWizard, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # self.setWindowTitle(u'测试用例设置向导')
        self.setGeometry(300, 200, 1000, 600)
        # self.addPage(self.createPreparePage())
        for i in self.parentWidget().checkDict.keys():
            page = self.parentWidget().checkDict.get(i).setup()
            if page:
                self.addPage(page)

    def stateToggled(self, state):
        sender = self.sender()

        if sender == self.loginBbkAccount:
            self.parentWidget().login = state
        elif sender == self.importBookData:
            self.parentWidget().datatype = state

        #self.parentWidget().datatype
        #self.parentWidget().login

        # def createPreparePage(self):
        #     page = QWizardPage()
        #     page.setTitle(u'测试准备')
        #     page.setSubTitle(u'选择测试开始前的准备动作。')
        #     page.setFinalPage(False)
        #
        #     self.importBookData = QCheckBox(u'导入三个同步课本资源')
        #     self.loginBbkAccount = QCheckBox(u'登录BBK账号(部分模块需要登录账号)')
        #     self.importBookData.setChecked(self.parentWidget().datatype)
        #     self.loginBbkAccount.setChecked(self.parentWidget().login)
        #     self.importBookData.toggled[bool].connect(self.stateToggled)
        #     self.loginBbkAccount.toggled[bool].connect(self.stateToggled)
        #     self.importBookData.setEnabled(False)
        #     self.loginBbkAccount.setEnabled(False)
        #
        #     layout = QVBoxLayout()
        #     layout.addWidget(self.importBookData)
        #     layout.addWidget(self.loginBbkAccount)
        #     page.setLayout(layout)
        #     return page


class SetupExecuteThread(QThread):
    logged = pyqtSignal(unicode, str)
    setupExecuteDone = pyqtSignal(str)

    def __init__(self, adb, **args):
        super(SetupExecuteThread, self).__init__()
        self.adb = adb
        self.login = args.get('login')
        self.datatype = args.get('datatype')
        self.getlog = args.get('getlog')
        self.executor = args.get('executor')
        self.workout = args.get('workout')

    def run(self):
        self.log(u'正在设置设备')
        start = time.time()
        if self.login:
            # self.log(u'登录BBK账号')
            # login_bbk_account(self.adb)
            pass

        if self.datatype:
            # self.log(u'导入书本资源数据')
            pass
        if self.executor:
            for item in self.executor.values():
                item.execute(self.log)
        self.log(u'所有任务完成，共耗时{0}秒'.format(round(time.time() - start, 3)))
        self.setupExecuteDone.emit(self.workout)

    def log(self, text, color='black'):
        self.logged.emit(text, color)


class ChildWindow(QWidget):
    def __init__(self, adb, packages):
        super(ChildWindow, self).__init__()

        self.adb = adb
        self.packages = packages

        self.info = collections.OrderedDict()
        self.info['序列号'] = get_prop(self.adb, 'ro.serialno')
        self.info['型号'] = get_prop(self.adb, 'ro.product.model')
        self.info['Android版本'] = get_prop(self.adb, 'ro.build.version.release')
        self.info['版本号'] = get_prop(self.adb, 'ro.build.version.incremental')
        self.info['版本类型'] = get_prop(self.adb, 'ro.build.type')
        self.info['制造商'] = get_prop(self.adb, 'ro.product.manufacturer')
        self.info['平台'] = get_prop(self.adb, 'ro.board.platform')

        self.workout = os.path.join(workdir, 'out')
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)
        self.workout = os.path.join(self.workout, self.info['序列号'])
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)
        self.workout = os.path.join(self.workout, self.info['版本号'])
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)
        # 开始时间
        self.workout = os.path.join(self.workout, time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))
        if not os.path.exists(self.workout):
            os.mkdir(self.workout)

        self.executor = collections.OrderedDict()
        for i, cls in enumerate(runner.Executor.__subclasses__()):
            self.executor[i] = cls(self)

        self.initUI()

    def initUI(self):
        self.message = QTextEdit()
        self.message.setReadOnly(True)
        self.devinfo = QTableWidget(7, 2)
        self.devinfo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.devinfo.setSelectionBehavior(QTableWidget.SelectRows)
        self.devinfo.setSelectionMode(QTableWidget.SingleSelection)
        self.devinfo.setAlternatingRowColors(True)
        self.devinfo.verticalHeader().setVisible(False)
        self.devinfo.horizontalHeader().setStretchLastSection(True)
        self.devinfo.horizontalHeader().setVisible(False)
        for i, (key, value) in enumerate(self.info.items()):
            self.devinfo.setItem(i, 0, QTableWidgetItem(unicode(key)))
            self.devinfo.setItem(i, 1, QTableWidgetItem(value))

        splitter1 = QSplitter(Qt.Vertical)
        splitter2 = QSplitter(Qt.Horizontal)

        splitter1.addWidget(self.devinfo)
        #mwidget = QWidget()
        #mwidget.setLayout(self.createSelectLayout())

        splitter2.addWidget(self.createSelectLayout())
        splitter2.addWidget(self.message)
        splitter1.addWidget(splitter2)
        layout = QVBoxLayout()
        layout.addWidget(splitter1)
        self.setLayout(layout)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.userFriendlyCurrentDevice())

    def loginAccounts(self):
        # 登录bbk账号
        pass

    def importData(self):
        # 导入资源数据
        pass

    def updateResultButton(self, path):
        self.reportButton.setEnabled(True)

    def executeBuildSettings(self):
        self.login = False
        self.datatype = True
        self.getlog = False
        temp = BuildSetupWizard(self).exec_()
        if temp:
            self.okButton.setEnabled(True)

    def executeBuildTest(self):
        if self.checkDict:
            self.t = SetupExecuteThread(self.adb, executor=self.checkDict, login=self.login,
                                        datatype=self.datatype, getlog=self.getlog, workout=self.workout)
            self.t.logged.connect(self.showMessage)
            self.t.setupExecuteDone.connect(self.updateResultButton)
            self.t.start()

    def userFriendlyCurrentDevice(self):
        return self.info.get('序列号')

    def closeEvent(self, event):
        if QMessageBox.question(self, u'断开连接', u'是否断开与设备 {0} 的连接'.format(self.userFriendlyCurrentDevice()),
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def showMessage(self, text, color='black'):
        strft = time.strftime('%Y-%m-%d %H:%M:%S')
        line = u'<font color="{0}">{1} {2}</font>\n'.format(color, strft, text)
        self.message.append(line)

    def createSelectLayout(self):
        # self.listWidget = QListWidget(self)
        # for i in self.executor.keys():
        #     print i,self.executor.get(i)
        #     item = QListWidgetItem(self.executor.get(i).title())
        #     item.setCheckState(Qt.Unchecked)
        #     item.setData(1, QVariant(i))
        #     self.listWidget.addItem(item)
        self.settingButton = QPushButton(u'参数设置')
        self.settingButton.clicked.connect(self.buttonClicked)
        self.okButton = QPushButton(u'开始测试')
        self.okButton.clicked.connect(self.buttonClicked)
        self.okButton.setEnabled(False)
        self.selallButton = QPushButton(u'全选')
        self.selallButton.clicked.connect(self.buttonClicked)
        self.disallButton = QPushButton(u'反选')
        self.disallButton.clicked.connect(self.buttonClicked)
        self.reportButton = QPushButton(u'查看报告')
        self.reportButton.clicked.connect(self.buttonClicked)
        self.reportButton.setEnabled(False)
        buttonBox = QDialogButtonBox(Qt.Vertical)
        buttonBox.addButton(self.settingButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.okButton, QDialogButtonBox.ActionRole)
        # buttonBox.addButton(self.selallButton, QDialogButtonBox.ActionRole)
        # buttonBox.addButton(self.disallButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.reportButton, QDialogButtonBox.ActionRole)
        #layout = QHBoxLayout()
        # layout.addWidget(self.listWidget)
        # layout.addWidget(buttonBox)
        return buttonBox

    def buttonClicked(self):
        sender = self.sender()
        if sender==self.settingButton:
            self.checkDict = self.executor
            self.executeBuildSettings()
        if sender == self.okButton:
            if self.reportButton.isEnabled():
                self.reportButton.setEnabled(False)
            self.checkDict = self.executor
            # for i in range(self.listWidget.count()):
            #     item = self.listWidget.item(i)
                # if item.checkState() == Qt.Checked:
                # self.checkDict[i] = copy.copy(self.executor.get(item.data(1).toPyObject()))
            self.executeBuildTest()
        elif sender == self.selallButton:
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setCheckState(Qt.Checked)
        elif sender == self.disallButton:
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setCheckState(Qt.Unchecked)
        elif sender == self.reportButton:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.workout))
