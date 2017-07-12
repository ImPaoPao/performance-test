# -*- coding: utf-8 -*-
import os
import re
import sys

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))


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
    adb.install(os.path.join(workdir, 'TestKit.apk'))
    adb.install(os.path.join(workdir, 'TestKitTest.apk'))
    packages = {}
    p = re.compile('INSTRUMENTATION_STATUS: stream=({.*})')
    cmd_str = 'am instrument -w -r   -e class com.eebbk.test.kit.PackageManagerProxy#getPackageList com.eebbk.test.kit.test/android.support.test.runner.AndroidJUnitRunner'
    results = adb.shell_open(cmd_str).stdout.readlines()
    for line in results:
        m = p.search(line)
        if m:
            packages = eval(m.groups()[0])
    return packages
