# -*- coding: utf-8 -*-

import os
import re
import shutil
import sys
import subprocess
import zipfile
import ConfigParser

from xml.etree.ElementTree import ElementTree, ParseError
from PyQt4.QtGui import *

workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

class Apk(object):

    def __init__(self, apkfile):
        self.file = apkfile
        self.name = os.path.basename(self.file)
        self.package = ''
        self.version = ''
        self.label = ''
        self.launcher = ''

        p = subprocess.Popen('\"{0}\" d badging \"{1}\"'.format(os.path.join(workdir, 'aapt'), self.file), stdout=subprocess.PIPE)
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

def getconfig(option, section='basic', path=os.path.join(workdir, 'config.ini')):
    if os.path.exists(path):
        cf = ConfigParser.ConfigParser()
        cf.read(path)
        if cf.has_option(section, option):
            return unicode(cf.get(section, option), 'utf-8')

def setconfig(option, value, section='basic', path=os.path.join(workdir, 'config.ini')):
    cf = ConfigParser.ConfigParser()
    if os.path.exists(path):
        cf.read(path)
    if not cf.has_section(section):
        cf.add_section(section)
    cf.set(section, option, value)
    with open(path, 'w') as f:
        cf.write(f)