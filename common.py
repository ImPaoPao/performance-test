# -*- coding: utf-8 -*-

import ConfigParser
import os
import re
import subprocess
import sys

import adbkit

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Apk(object):
    def __init__(self, apkfile):
        self.file = apkfile
        self.name = os.path.basename(self.file)
        self.package = ''
        self.version = ''
        self.label = ''
        self.launcher = ''

        p = subprocess.Popen('\"{0}\" d badging \"{1}\"'.format(os.path.join(workdir, 'aapt'), self.file),
                             stdout=subprocess.PIPE)
        for line in p.stdout.readlines():
            if line.startswith('package:'):
                m = re.search('name=\'(.*)\' versionCode=\'.*\' versionName=\'(.*)\'', line)
                if m:
                    g = m.groups()
                    self.package = g[0]
                    self.version = g[1]
            elif line.startswith('application-label:'):
                m = re.search('application-label:\'(.*)\'', line)
                if m:
                    self.label = m.groups()[0]
            elif line.startswith('application-label-zh_CN:'):
                m = re.search('application-label-zh_CN:\'(.*)\'', line)
                if m:
                    self.label = m.groups()[0]
            elif line.startswith('launchable-activity:'):
                m = re.search('name=\'(.*)\' +label=\'(.*)\'', line)
                if m:
                    self.launcher = m.groups()[0]


def getconfig(option, section='data', path=os.path.join(workdir, 'config.ini')):
    if os.path.exists(path):
        cf = ConfigParser.ConfigParser()
        cf.read(path)
        if cf.has_option(section, option):
            return unicode(cf.get(section, option), 'utf-8')


def setconfig(option, value, section='data', path=os.path.join(workdir, 'config.ini')):
    cf = ConfigParser.ConfigParser()
    if os.path.exists(path):
        cf.read(path)
    if not cf.has_section(section):
        cf.add_section(section)
    cf.set(section, option, value)
    with open(path, 'w') as f:
        cf.write(f)


def login_bbk_account(adb):
    print u'登录BBK账号'


def importdata(adb):
    print u'导入课本数据'
    data = []
    seldir = os.path.join(getconfig('datadir').encode('utf-8'))
    for name in os.listdir(seldir):
        size = 0L
        path = os.path.join(seldir, name)
        pimdir = None
        for dirpath, dirnames, names in os.walk(path):
            dirname = os.path.basename(dirpath)
            pimdir = dirpath
            size += sum([os.path.getsize(os.path.join(dirpath, name)) for name in names])
        if pimdir:
            data.append((size, pimdir))

    if data:
        m = re.search('[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+(\d+\.\d+)(\S+)[ ]+\d+', adb.shell_readlines('df sdcard')[-1])
        if m:
            z = lambda x, y: x * pow(1024, 'BKMGT'.find(y))
            g = m.groups()
            s = z(float(g[0]), g[1])
        else:
            s = 0
        if s > 12.3 * pow(1024, 3):
            data = [x for x in data if x[0] == max([i[0] for i in data])]
        else:
            data = [x for x in data if x[0] == min([i[0] for i in data])]

    pimdir = '/sdcard/小学/'
    if data:
        adb.push(seldir, pimdir)
    print seldir
    print pimdir


if __name__ == '__main__':
    print workdir
    print os.path.join(getconfig('datadir').encode('gb2312'))
    all_connect_devices = adbkit.devices()
    for device in all_connect_devices:
        if 'H8SM1700000022' in device['serialno']:
            adb = adbkit.Adb(device)
    importdata(adb)
