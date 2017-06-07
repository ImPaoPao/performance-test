# -*- coding: utf-8 -*-
import os
import threading
import time
import sys

import adbkit
from module import LauncherModule

WORK_OUT = os.path.join(os.path.expanduser('~'), 'eebbk-results')
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def run(adb, serialno, type):
    work_out = os.path.join(WORK_OUT, str(serialno), time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))
    LauncherModule(adb, work_out).execute()


def stop(adb, types):
    pass




if __name__ == "__main__":
    if len(sys.argv) > 1:
        device = adbkit.Device(serialno=sys.argv[1])
        adb = adbkit.Adb(device)
        run(adb,sys.argv[1],'module')
    else:
        # get connect devices
        threads = []
        all_connect_devices = adbkit.devices()
        for device in all_connect_devices:
            adb = adbkit.Adb(device)
            print device['serialno'], '.......threading...............'
            t = threading.Thread(target=run, args=(adb, device['serialno'], 'module'))
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
