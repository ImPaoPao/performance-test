# -*- coding: utf-8 -*-

import testplatform as platform
import sys
from PyQt4.QtGui import QApplication, QStyleFactory


def main():
    # QApplication.setStyle(QStyleFactory.create('cleanlooks'))
    app = QApplication(sys.argv)
    win = platform.MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
