# -*- coding: utf-8 -*-
import adbkit
import glob
import os
import re
import subprocess
import sys
import time

DATA_WORK_PATH = '/data/local/tmp/launch'


# filepath: selected package union
# packages: all package infos on device



def echo_to_file(adb, lines, path, append=True):
    cmd = '"echo %s >> %s"' if append else '"echo %s > %s"'
    for line in lines if type(lines) == list else [lines]:
        adb.shell(cmd % (line, path))
    else:
        print 'else touch'
        adb.shell('touch %s' % path)


def get_packages(adb):
    packages = {}
    clazz = 'com.eebbk.test.kit.PackageManagerProxy'
    method = 'getPackageList'
    extras = None
    apk_pkg = 'com.eebbk.test.kit.test'
    p = re.compile('INSTRUMENTATION_STATUS: stream=({.*})')
    cmd_str = 'am instrument -r -e class %s%s %s -w %s/android.support.test.runner.AndroidJUnitRunner' % (
        clazz, '#' + method if method else '', ' '.join(extras) if extras else '', apk_pkg)
    results = adb.shell_open(cmd_str).stdout.readlines()
    for line in results:
        m = p.search(line)
        if m:
            print 'get packages sucess '
            packages = eval(m.groups()[0])
    return packages

