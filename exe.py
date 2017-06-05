# -*- coding: utf-8 -*-
import adbkit
import codecs
import csv
import glob
import os
import platform
import re
import sys
import time
import threading

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
        # get connect devices
        threads=[]
        all_connect_devices=adbkit.devices()
        for device in all_connect_devices:
            adb = adbkit.Adb(device)
            print device['serialno'],'.......threading...............'
            t = threading.Thread(target=run,args=(adb,device['serialno'],'module'))
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()