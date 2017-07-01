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
from common import workdir, getconfig

import module
import launch
class BuildSetupWizard(QWizard):
    def __init__(self, parent):
        super(BuildSetupWizard, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(u'测试用例设置向导')
        self.setGeometry(300, 200, 800, 600)
        self.addPage(self.createPreparePage())
        for i in self.parentWidget().checkDict.keys():
            page = self.parentWidget().checkDict.get(i).setup()
            if page:
                self.addPage(page)

    def stateToggled(self, state):
        sender = self.sender()

        if sender == self.loginAccountsCheck:
            self.parentWidget().login = state
        elif sender == self.importDataCheck:
            self.importDataCombo.setEnabled(state)
            if state:
                self.parentWidget().datatype = str(self.importDataCombo.currentText())
            else:
                self.parentWidget().datatype = None
        elif sender == self.openLogCheck:
            self.parentWidget().getlog = state

    def itemActivated(self, item):
        sender = self.sender()

        if sender == self.importDataCombo:
            self.parentWidget().datatype = str(item)

    def createPreparePage(self):
        page = QWizardPage()
        page.setTitle(u'测试准备')
        page.setSubTitle(u'选择测试开始前的准备动作。')
        page.setFinalPage(True)
        edittext = QLabel()
        edittext.setText(u'待扩展补充.......例如:安装三方应用......')
        layout = QVBoxLayout()
        layout.addWidget(edittext)
        layout.addWidget(edittext)
        page.setLayout(layout)
        return page


class SetupExecuteThread(QThread):
    logged = pyqtSignal(unicode, str)

    def __init__(self, adb, **args):
        super(SetupExecuteThread, self).__init__()

        self.adb = adb
        self.login = args.get('login')
        self.datatype = args.get('datatype')
        self.getlog = args.get('getlog')
        self.executor = args.get('executor')
        self.workout = args.get('workout')
        print self.adb
        print 'SetupExecuteThread.......'

    def run(self):
        self.log(u'正在设置设备')
        # self.adb.kit.wakeup()
        # self.adb.kit.disablekeyguard()
        # self.adb.kit.keepscreenon()

        start = time.time()
        update = True
        # if self.executor:
        #     for item in self.executor.values():
        #         if item.title() == '系统升级':
        #             self.log(u'正在执行{0}'.format(item.title()))
        #             if not item.execute(self.log):
        #                 update = False
        if update:
            # if self.login:
            #     self.log(u'正在登录预置的应用帐号')
            #     loginaccounts(self.adb)

            # if self.datatype:
            #     self.log(u'正在导入预置的用户数据')
            #     importdata(self.adb, self.datatype)

            # if self.getlog:
            #     self.log(u'正在打开离线日志开关')
            #     common.openlog(self.adb)
            print 'exeutor run.........'
            if self.executor:
                for item in self.executor.values():
                    # if item.title() != '系统升级':
                    #     self.log(u'正在执行{0}'.format(item.title()))
                    print 'item',item
                    item.execute(self.log)
        self.log(u'正在生成测试报告')
        # chart.run(self.workout, 'test')

        self.log(u'所有任务完成，共耗时{0}秒'.format(round(time.time() - start, 3)))

    def log(self, text, color='black'):
        self.logged.emit(text, color)


from tools import get_prop


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
        #开始时间
        self.workout = os.path.join(self.workout,time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))
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

        mwidget = QWidget()
        mwidget.setLayout(self.createSelectLayout())
        splitter2.addWidget(mwidget)
        splitter2.addWidget(self.message)
        splitter1.addWidget(splitter2)
        layout = QVBoxLayout()
        layout.addWidget(splitter1)
        self.setLayout(layout)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.userFriendlyCurrentDevice())

    def loginAccounts(self):
        if QMessageBox.question(self, u'登录帐号', u'<p>是否登录预置应用帐号</p><p>如需登录请先切换至英文输入法</p>',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
            self.t = SetupExecuteThread(self.adb, login=True)
            self.t.logged.connect(self.showMessage)
            self.t.start()

    def importData(self):
        datadir = getconfig('datadir')
        if os.path.exists(datadir):
            items = os.listdir(datadir)
            items = [x for x in items if os.path.isdir(os.path.join(datadir, x))]
            item, ok = QInputDialog.getItem(self, u'导入数据', u'选择数据类型：', items, 0, False)
            if ok and item:
                self.t = SetupExecuteThread(self.adb, datatype=str(item))
                self.t.logged.connect(self.showMessage)
                self.t.start()

    def executeBuildTest(self):
        self.login = False
        self.datatype = None
        self.getlog = False
        if BuildSetupWizard(self).exec_() and self.checkDict:
            self.t = SetupExecuteThread(self.adb, executor=self.checkDict, login=self.login,
                                        datatype=self.datatype, getlog=self.getlog, workout=self.workout)
            self.t.logged.connect(self.showMessage)
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
        self.listWidget = QListWidget(self)
        for i in self.executor.keys():
            item = QListWidgetItem(self.executor.get(i).title())
            item.setCheckState(Qt.Unchecked)
            item.setData(1, QVariant(i))
            self.listWidget.addItem(item)
        self.okButton = QPushButton(u'运行')
        self.okButton.clicked.connect(self.buttonClicked)
        self.selallButton = QPushButton(u'全选')
        self.selallButton.clicked.connect(self.buttonClicked)
        self.disallButton = QPushButton(u'反选')
        self.disallButton.clicked.connect(self.buttonClicked)
        # self.upButton = QPushButton(u'上移')
        # self.upButton.clicked.connect(self.buttonClicked)
        # self.downButton = QPushButton(u'下移')
        # self.downButton.clicked.connect(self.buttonClicked)
        buttonBox = QDialogButtonBox(Qt.Vertical)
        buttonBox.addButton(self.okButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.selallButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.disallButton, QDialogButtonBox.ActionRole)
        # buttonBox.addButton(self.upButton, QDialogButtonBox.ActionRole)
        # buttonBox.addButton(self.downButton, QDialogButtonBox.ActionRole)

        layout = QHBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addWidget(buttonBox)
        return layout

    def buttonClicked(self):
        sender = self.sender()
        print u'运行?: ', sender == self.okButton
        if sender == self.okButton:
            self.checkDict = {}
            for i in range(self.listWidget.count()):
                item = self.listWidget.item(i)
                if item.checkState() == Qt.Checked:
                    self.checkDict[i] = copy.copy(self.executor.get(item.data(1).toPyObject()))
            print u'选中的测试项',self.checkDict
            self.executeBuildTest()
        elif sender == self.selallButton:
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setCheckState(Qt.Checked)
        elif sender == self.disallButton:
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setCheckState(Qt.Unchecked)
