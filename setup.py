# -*- coding: utf-8 -*-
import py2exe
import os
import shutil
import sys
import zipfile
from distutils.core import setup
from glob import glob
from os.path import dirname, join

from common import getconfig

if len(sys.argv) == 1:
    sys.exit(2)

if sys.argv[1] == 'py2exe':
    with open('v.txt', 'r') as f:
        version = f.readline().strip()

    options = {
        'py2exe': {
            'includes': [
                'sip',
            ],
            'excludes': [
                '_gtkagg',
                '_tkagg',
                '_agg2',
                '_cairo',
                '_cocoaagg',
                '_fltkagg',
                '_gtk',
                '_gtkcairo',
                '_ufuncs_cxx',
                'tcl',
                'Tkconstants',
                'Tkinter'
            ],
            'dll_excludes': [
                'MSVCP90.dll',
                'libgdk-win32-2.0-0.dll',
                'libgobject-2.0-0.dll',
                'pywintypes27.dll',
                'tcl85.dll',
                'tk85.dll'
            ]
        }
    }

    data_files = []
    data_files.append(('.', [
        'busybox',
        'config.ini',
        'TestKit.apk',
        'TestKitTest.apk',
        'adb.exe',
        'aapt.exe',
        'AdbWinApi.dll',
        'AdbWinUsbApi.dll',
        'logo.ico',
        'v.txt',
        'readme.txt',
        'testcase.ini'
    ]))
    data_files.append(('module', glob(join('module', '*'))))
    data_files.append(('freememory', glob(join('freememory', '*'))))
    data_files.append(('launch', glob(join('launch', '*'))))
    setup(
        name='testplat',
        version=version,
        console=[{
            'script': 'start.py',
            'icon_resources': [(1, 'logo.ico')]
        }],
        windows=[{
            'script': 'upgrade.py',
            'icon_resources': [(1, 'logo.ico')]
        }],
        options=options,
        data_files=data_files
    )

    # rename files
    shutil.move(join('dist', 'start.exe'), join('dist', 'BbkTestPlatform.exe'))
    shutil.move(join('dist', 'upgrade.exe'), join('dist', 'BbkPlatformUpdate.exe'))

if sys.argv[1] in ['dist', 'publish']:
    f = zipfile.ZipFile('dist.zip', 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, names in os.walk('dist'):
        if not dirpath == join('dist', 'out'):
            for name in names:
                zippath = os.sep.join(dirpath.split(os.sep)[1:])
                f.write(join(dirpath, name), join(zippath, name))
    f.close()

if sys.argv[1] in ['publish']:
    remote = getconfig('distdir').encode('gb2312')
    shutil.copy('dist.zip', remote)
