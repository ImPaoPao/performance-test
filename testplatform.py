# -*- coding: utf-8 -*-


import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import adbkit

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()


    def initUI(self):
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.createActions()
        self.createMenus()
        self.updateMenus()
        self.setWindowTitle(u'自动化测试平台开发版')
        self.setWindowIcon(QIcon('logo.png'))
        self.setUnifiedTitleAndToolBarOnMac(True)

    def about(self):
        with open(os.path.join(workdir, 'v.txt'), 'r') as f:
            ver = f.readline().strip()
        QMessageBox.about(self, u'测试平台',
                          u'<p>性能测试<p>'
                          u'<p>平台版本：{0}'.format(ver))

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)


    def createMdiChild(self, adb, packages):
        mdiChild = executor.ChildWindow(adb, packages)
        self.mdiArea.addSubWindow(mdiChild)
        return mdiChild

    def createActions(self):
        self.connectDeviceAct = QAction(QIcon('images/android.png'), u'连接设备', self,
                                        shortcut='Ctrl+Shift+C',
                                        statusTip=u'连接在线的设备',
                                        triggered='')
        self.aboutAct = QAction(u'关于', self,
                                shortcut='F1',
                                triggered=self.about)

    def createMenus(self):
        self.deviceMenu = self.menuBar().addMenu(u'设备(&D)')
        self.deviceMenu.addAction(self.connectDeviceAct)
        self.helpMenu = self.menuBar().addMenu(u'帮助(&H)')
        self.helpMenu.addAction(self.aboutAct)

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def setActiveSubWindow(self, window):


        if window:
            self.mdiArea.setActiveSubWindow(window)
