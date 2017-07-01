# -*- coding: utf-8 -*-
import glob
import os
import re
import subprocess
import sys
import time

import adbkit

# filepath: selected package union
# packages: all package infos on device

def get_prop(adb, key):
    return adb.adb_readline('shell getprop %s ' % key)


def set_prop(adb, key):
    return adb.adb_readline('shell setprop %s ' % key)


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
    cmd_str = 'am instrument -w -r   -e class com.eebbk.test.kit.PackageManagerProxy#getPackageList com.eebbk.test.kit.test/android.support.test.runner.AndroidJUnitRunner'
    results = adb.shell_open(cmd_str).stdout.readlines()
    for line in results:
        m = p.search(line)
        if m:
            print 'get packages sucess '
            packages = eval(m.groups()[0])
    return packages

