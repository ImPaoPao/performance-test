# -*- coding: utf-8 -*-

import collections
import os
import sys
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import adbkit
from blockcanary import ModuleMonitor
from tools import get_prop

reload(sys)
sys.setdefaultencoding('utf-8')
workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
import copy


class BlockExecuteThread(QThread):
    logged = pyqtSignal(unicode, str)
    setupExecuteDone = pyqtSignal(str)

    def __init__(self, child, **args):
        super(BlockExecuteThread, self).__init__()
        self.adb = child.adb
        self.workout = args.get('workout')

    def run(self):
        ModuleMonitor(self.adb,self.workout)
        #self.log(u'所有任务完成，共耗时{0}秒'.format(round(time.time() - start, 3)))
        #self.setupExecuteDone.emit(self.workout)

    def log(self, text, color='black'):
        self.logged.emit(text, color)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.seed = 23
        self.count = 100000
        self.throttle = 100
        self.devices = []
        self.adbs = []
        self.retry = False
        self.single = False
        self.initUI()

    def initUI(self):
        devices = adbkit.devices()
        if devices:
            for device in devices:
                serialno = device['serialno']
                self.devices.append(serialno)
                # adb = adbkit.Adb(adbkit.Device(serialno=serialno))
                # self.adbs.append(adb)
        self.tempdevices = copy.copy(self.devices)
        mdiChild = QWidget()
        check = QCheckBox(u'导出上次的卡顿数据(手动操作设备产生的卡顿数据)')
        self.okButton = QPushButton(u'运行')
        self.okButton.clicked.connect(self.buttonClicked)
        headerLayout = QHBoxLayout()  # QGridLayout()
        headerLayout.addWidget(check)
        headerLayout.addStretch()
        headerLayout.addWidget(self.okButton)

        check.toggled[bool].connect(self.retryChecked)
        self.radio1 = QRadioButton(u'整机Monkey')
        self.radio1.setChecked(not self.single)
        self.radio1.toggled[bool].connect(self.radio1Toggled)
        self.radio3 = QRadioButton(u'APPStart工具遍历')
        self.radio3.setEnabled(False)
        # self.radio3.setChecked(self.install)
        # self.radio3.toggled[bool].connect(self.radio3Toggled)
        self.radio2 = QRadioButton(u'单包Monkey(全部BBK应用)')
        self.radio2.setChecked(self.single)
        self.radio2.toggled[bool].connect(self.radio2Toggled)
        self.edit1 = QLineEdit(str(self.seed))
        self.edit1.setValidator(QIntValidator())
        self.edit1.textChanged[str].connect(self.edit1Changed)
        self.edit2 = QLineEdit(str(self.throttle))
        self.edit2.setValidator(QIntValidator())
        self.edit2.textChanged[str].connect(self.edit2Changed)
        self.edit3 = QLineEdit(str(self.count))
        self.edit3.setValidator(QIntValidator())
        self.edit3.textChanged[str].connect(self.edit3Changed)
        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(u'种子数'), 0, 0)
        gridLayout.addWidget(self.edit1, 0, 1)
        gridLayout.addWidget(QLabel(u'事件间隔'), 1, 0)
        gridLayout.addWidget(self.edit2, 1, 1)
        gridLayout.addWidget(QLabel(u'事件次数'), 2, 0)
        gridLayout.addWidget(self.edit3, 2, 1)
        itemLayout = QVBoxLayout()
        itemLayout.addWidget(self.radio1)
        itemLayout.addWidget(self.radio2)
        itemLayout.addWidget(self.radio3)

        itemLayout.addStretch()
        itemLayout.addLayout(gridLayout)
        self.itemGroup = QGroupBox(u'应用卡顿模拟用户操作')
        self.itemGroup.setLayout(itemLayout)
        self.list = QListWidget()
        self.list.itemChanged.connect(self.itemChanged)
        for device in self.devices:
            item = QListWidgetItem(device)
            item.setCheckState(Qt.Checked)
            item.setData(1, QVariant(device))
            self.list.addItem(item)
        listLayout = QVBoxLayout()
        listLayout.addWidget(self.list)
        self.listGroup = QGroupBox(u'选择需要执行操作的设备')
        self.listGroup.setLayout(listLayout)

        itemLayout = QHBoxLayout()
        itemLayout.addWidget(self.itemGroup)
        itemLayout.addWidget(self.listGroup)
        itemLayout.setStretch(0, 1)
        itemLayout.setStretch(1, 3)
        layout = QVBoxLayout()
        layout.addLayout(headerLayout)
        layout.addLayout(itemLayout)
        mdiChild.setLayout(layout)
        self.setCentralWidget(mdiChild)
        self.show()

    def retryChecked(self, checked):
        self.retry = checked
        self.itemGroup.setDisabled(self.retry)

    def radio1Toggled(self, checked):
        self.single = False
        self.count = 1000000
        self.edit3.setText(str(self.count))

    def radio2Toggled(self, checked):
        self.single = True
        self.count = 200000
        self.edit3.setText(str(self.count))

    def radio3Toggled(self, checked):
        self.single = False
        self.count = 1000000
        self.edit3.setText(str(self.count))

    def edit1Changed(self, text):
        if str(text).isdigit():
            self.seed = int(text)
        else:
            self.edit1.undo()

    def edit2Changed(self, text):
        if str(text).isdigit():
            self.throttle = int(text)
        else:
            self.edit2.undo()

    def edit3Changed(self, text):
        if str(text).isdigit():
            self.count = int(text)
        else:
            self.edit3.undo()

    def itemChanged(self, item):
        serialno = str(item.data(1).toPyObject())
        if serialno == 'selall':
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(item.checkState())
        else:
            if item.checkState() == Qt.Checked:
                if serialno not in self.devices:
                    self.devices.append(serialno)
            else:
                self.devices.remove(serialno)

    def buttonClicked(self):
        sender = self.sender()
        if sender == self.okButton:
            self.executeBuildTest()

    def executeBuildTest(self):
        print self.tempdevices
        print u'选中:', self.devices
        devices = adbkit.devices()
        if self.tempdevices and devices:
            if not self.devices:
                QMessageBox.question(self, 'Message', u'请选择要执行的设备', QMessageBox.Yes)
            else:
                for device in self.devices:
                    adb = adbkit.Adb(adbkit.Device(serialno=device['serialno']))
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
                    self.workout = os.path.join(self.workout,
                                                time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))
                    if not os.path.exists(self.workout):
                        os.mkdir(self.workout)

                    self.t = BlockExecuteThread(self)
                    self.t.setupExecuteDone.connect(self.updateResultButton)
                    self.t.start()

        else:
            result = QMessageBox.question(self, 'Message', u'请重新插拔USB,确定设备连接正常再点击确定按钮', QMessageBox.Yes)
            if result:
                devices = adbkit.devices()
                if devices:
                    for device in devices:
                        serialno = device['serialno']
                        if serialno not in devices:
                            self.devices.append(serialno)
                            item = QListWidgetItem(serialno)
                            item.setCheckState(Qt.Checked)
                            item.setData(1, QVariant(serialno))
                            self.list.addItem(item)
                        self.tempdevices = copy.copy(self.devices)
                        # else:
                        #     QMessageBox.question(self, 'Message', u'设备连接异常...请检查...', QMessageBox.Yes)
                        # else:
                        #     result = QMessageBox.question(self, 'Message', u'设备连接异常，请重新连接', QMessageBox.Yes)
                        # self.info = collections.OrderedDict()
                        # self.info['序列号'] = get_prop(self.adb, 'ro.serialno')
                        # self.info['型号'] = get_prop(self.adb, 'ro.product.model')
                        # self.info['Android版本'] = get_prop(self.adb, 'ro.build.version.release')
                        # self.info['版本号'] = get_prop(self.adb, 'ro.build.version.incremental')
                        # self.info['版本类型'] = get_prop(self.adb, 'ro.build.type')
                        # self.info['制造商'] = get_prop(self.adb, 'ro.product.manufacturer')
                        # self.info['平台'] = get_prop(self.adb, 'ro.board.platform')
                        #
                        # if self.checkDict:
                        #     self.workout = os.path.join(workdir, 'out')
                        #     if not os.path.exists(self.workout):
                        #         os.mkdir(self.workout)
                        #     self.workout = os.path.join(self.workout, self.info['序列号'])
                        #     if not os.path.exists(self.workout):
                        #         os.mkdir(self.workout)
                        #     self.workout = os.path.join(self.workout, self.info['版本号'])
                        #     if not os.path.exists(self.workout):
                        #         os.mkdir(self.workout)
                        #     # 开始时间
                        #     self.workout = os.path.join(self.workout, time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))
                        #     if not os.path.exists(self.workout):
                        #         os.mkdir(self.workout)
                        #
                        #     self.t = SetupExecuteThread(self.adb, executor=self.checkDict, login=self.login,
                        #                                 datatype=self.datatype, getlog=self.getlog, workout=self.workout)
                        #     self.t.logged.connect(self.showMessage)
                        #     self.t.setupExecuteDone.connect(self.updateResultButton)
                        #     self.t.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
