# -*- coding: utf-8 -*-

import os
import sys

from PyQt4.QtGui import QApplication

import testplatform as platform


def main():
    # QApplication.setStyle(QStyleFactory.create('cleanlooks'))
    app = QApplication(sys.argv)
    win = platform.MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    # mfile = r'D:\bbk-test-center\EebbkTestCenter\performance-test\testcase.ini'
    # if os.path.exists(mfile):
    #     with open(r'D:\pendant.txt','wb') as rf:
    #         with open(mfile, 'rb') as f:
    #             for line in f:
    #                 if line.startswith('#'):
    #                     continue
    #                 line = line.strip('')
    #                 list = line.split(' ')
    #                 clsname = list[0]
    #                 metname = list[1]
    #                 pkg = list[2]
    #                 label = list[3]
    #                 nlist = ['com.eebbk.test.performance', clsname, metname, metname, 5, pkg, 0, 0, 0]
    #                 rf.write(" ".join(str(i) for i in nlist))
    #                 rf.write("\n")
