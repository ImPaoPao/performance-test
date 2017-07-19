# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import adbkit
import executor
from common import workdir
from tools import get_packages
import threading

class QueryDeviceThread(QThread):
    queryDeviceDone = pyqtSignal(tuple)

    def __init__(self):
        super(QueryDeviceThread, self).__init__()

    def run(self):
        self.queryDeviceDone.emit(adbkit.devices())


class ConnectDeviceThread(QThread):
    connectDeviceDone = pyqtSignal(str, adbkit.Adb)
    connectDeviceFail = pyqtSignal(str)

    def __init__(self, serialno):
        super(ConnectDeviceThread, self).__init__()
        self.serialno = serialno

    def run(self):
        adb = adbkit.Adb(adbkit.Device(serialno=self.serialno))
        if adb.get_state() != 'device':
            self.connectDeviceFail.emit(self.serialno)
        else:
            self.connectDeviceDone.emit(self.serialno, adb)


class QueryPackageThread(QThread):
    queryPackageDone = pyqtSignal(adbkit.Adb, dict)

    def __init__(self, adb):
        super(QueryPackageThread, self).__init__()
        self.adb = adb

    def run(self):
        packages = get_packages(self.adb)
        testpkgs = [line[8:].strip() for line in
                    self.adb.adb_readlines('shell pm list packages -s | findstr com.e*bbk')]
        packages = dict([x for x in packages.items() if x[0] in testpkgs])
        # pkg {'label':***,'version':version}
        self.queryPackageDone.emit(self.adb, packages)


# class QueryUpdateThread(QThread):
#     queryUpdateDone = pyqtSignal(str, str)
#
#     def __init__(self):
#         super(QueryUpdateThread, self).__init__()
#
#     def run(self):
#         remote = getconfig('distdir').encode('gb2312')
#         exefile = 'PlatformUpdate.exe' if sys.platform == 'win32' else 'PlatformUpdate'
#
#         if os.path.exists(remote):
#             with zipfile.ZipFile(os.path.join(remote, 'dist.zip')) as zf:
#                 newver = zf.open('v.txt').readline().strip()
#                 with open(os.path.join(workdir, exefile), 'wb') as f:
#                     f.write(zf.read(exefile))
#             with open(os.path.join(workdir, 'v.txt'), 'r') as f:
#                 locver = f.readline().strip()
#
#             self.queryUpdateDone.emit(locver, newver)


class MainWindow(QMainWindow):
    oneDeviceCreateChildWindowDone = pyqtSignal(str)
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.update()

    def initUI(self):
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle(u'性能测试工具')
        self.setWindowIcon(QIcon('logo.png'))
        self.setUnifiedTitleAndToolBarOnMac(True)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def connectDevice(self):
        self.qdt = QueryDeviceThread()
        self.qdt.queryDeviceDone.connect(self.onDeviceQuery)
        self.qdt.start()

    def onDeviceQuery(self, devices):
        if devices:
            if len(devices) == 1:
                serialno = devices[0]['serialno']
                if serialno:
                    self.statusLabel.setText(u'正在连接设备 {0} '.format(serialno))
                    self.cdt = ConnectDeviceThread(serialno)
                    self.cdt.connectDeviceDone.connect(self.onDeviceConnect)
                    self.cdt.connectDeviceFail.connect(self.onDeviceConnect)
                    self.cdt.start()
            else:
                serialnos = []
                for device in devices:
                    serialnos.append(device['serialno'])
                item, ok = QInputDialog.getItem(self, u'选择设备', u'设备列表：', serialnos, 0, False)
                serialno = item if ok and item else None
                # self.checkedDevices = []
                # deviceDialog = DeviceDialog(self,serialnos)
                # if deviceDialog.exec_():
                #     for serialno in self.checkedDevices:
                #         if serialno:
                #             self.statusLabel.setText(u'正在连接设备 {0}'.format(serialno))
                #             self.cdt = ConnectDeviceThread(serialno)
                #             self.cdt.connectDeviceDone.connect(self.onDeviceConnect)
                #             self.cdt.connectDeviceFail.connect(self.onDeviceConnect)
                #             self.cdt.start()

                if serialno:
                    self.statusLabel.setText(u'正在连接设备 {0}'.format(serialno))
                    self.cdt = ConnectDeviceThread(serialno)
                    self.cdt.connectDeviceDone.connect(self.onDeviceConnect)
                    self.cdt.connectDeviceFail.connect(self.onDeviceConnect)
                    self.cdt.start()

        else:
            QMessageBox.information(self, u'提示', u'无法获取在线设备列表，请连接设备并打开USB调试后重试')

    def onDeviceConnect(self, serialno, adb=None):
        if adb:
            self.qpt = QueryPackageThread(adb)
            self.qpt.queryPackageDone.connect(self.onPackageQuery)
            self.qpt.start()
        else:
            QMessageBox.information(self, u'提示', u'无法连接设备 {0}，请确保该设备唯一在线且处于空闲状态'.format(serialno))

    def onPackageQuery(self, adb, packages):
        self.statusLabel.clear()
        mdiChild = self.createMdiChild(adb, packages)
        mdiChild.show()

    def loginAccounts(self):
        if self.activeMdiChild():
            self.activeMdiChild().loginAccounts()

    def importData(self):
        if self.activeMdiChild():
            self.activeMdiChild().importData()


    def about(self):
        with open(os.path.join(workdir, 'v.txt'), 'r') as f:
            ver = f.readline().strip()
        QMessageBox.about(self, u'性能测试工具',
                          u'<p>性能测试<p>'
                          u'<p></p>'
                          u'<p>工具版本：{0}'.format(ver))

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = '%d %s' % (i + 1, child.userFriendlyCurrentDevice())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def createMdiChild(self, adb, packages):
        mdiChild = executor.ChildWindow(adb, packages)
        self.mdiArea.addSubWindow(mdiChild)
        return mdiChild

    def createActions(self):
        self.connectDeviceAct = QAction(QIcon(''), u'连接设备', self,
                                        shortcut='Ctrl+Shift+C',
                                        statusTip=u'连接在线的设备',
                                        triggered=self.connectDevice)
        self.aboutAct = QAction(u'关于', self,
                                shortcut='F1',
                                triggered=self.about)

    def createMenus(self):
        self.deviceMenu = self.menuBar().addMenu(u'设备(&D)')
        self.deviceMenu.addAction(self.connectDeviceAct)
        self.helpMenu = self.menuBar().addMenu(u'帮助(&H)')
        self.helpMenu.addAction(self.aboutAct)

    def createToolBars(self):
        pass


    def createStatusBar(self):
        self.statusLabel = QLabel()
        self.statusBar().addPermanentWidget(self.statusLabel)
        self.statusBar().showMessage(u'就绪')

    def readSettings(self):
        settings = QSettings('bbk', 'TestPlatform')
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(600, 400))
        self.move(pos.toPyObject())
        self.resize(size.toPyObject())

    def writeSettings(self):
        settings = QSettings('bbk', 'TestPlatform')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)


class DeviceDialog(QDialog):
    def __init__(self,parent ,serialnos):
        QDialog.__init__(self,parent)
        self.serialnos = serialnos
        self.checkedDevices =self.parent().checkedDevices
        self.initUi()

    def initUi(self):
        self.setWindowTitle(u'设备列表')
        deviceLayout = QVBoxLayout()
        deviceLayout.addWidget(QLabel(u'请选择要连接的设备:'))
        self.listWidget = QListWidget(self)
        for i in self.serialnos:
            item = QListWidgetItem(i)
            item.setCheckState(Qt.Unchecked)
            item.setData(1, QVariant(i))
            self.listWidget.addItem(item)
        self.listWidget.itemChanged.connect(self.itemChanged)
        deviceLayout.addWidget(self.listWidget)
        buttonBox = QDialogButtonBox(parent=self)
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        deviceLayout.addWidget(buttonBox)
        self.setLayout(deviceLayout)
        print 'self',self
        print '%%%%%%',self.parent().checkedDevices

    def itemChanged(self, item):
        serialno = str(item.data(1).toPyObject())
        if item.checkState() == Qt.Checked:
            if serialno not in self.checkedDevices:
                self.checkedDevices.append(serialno)
        else:
            if serialno in self.checkedDevices:
                self.checkedDevices.remove(serialno)
        print u'选中：', self.checkedDevices