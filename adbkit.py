# -*- coding: utf-8 -*-
import os
import re
import subprocess
import time
import platform
import threading
DATA_LOCAL_TMP='/data/local/tmp'


def devices(host=None):
    results = []
    pattern = re.compile('^(.+?)\s+device (usb:(.+?)\s+)?product:(.+?)\s+model:(.+?)\s+device:(.+?)\s+(feature:.+?)?')
    for line in subprocess.Popen('adb devices -l', shell=True, stdout=subprocess.PIPE).stdout.readlines():
        m = pattern.search(line)
        if m:
            g = m.groups()
            results.append(Device(g[0], g[3], g[4], g[5]))
    # filter available device serialno
    return tuple(sorted([i for i in results if i['serialno'] != i['model'].replace('_', '')]))


class Adb(object):
    def __init__(self, device):
        self.device = device

    def __adb_open(self, cmd):
        return self.popen('adb -s %s %s' % (self.device['serialno'], cmd), '')

    def __shell_open(self, cmd):
        return self.__adb_open('shell %s' % cmd)

    def __adb_readline(self, cmd):
        return self.__adb_open(cmd).stdout.readline().strip()

    def __shell_readline(self, cmd):
        return self.__shell_open(cmd).stdout.readline().strip()

    def __adb_readlines(self, cmd):
        return self.__adb_open(cmd).stdout.readlines()

    def __shell_readlines(self, cmd):
        return self.__shell_open(cmd).stdout.readlines()

    def __adb(self, cmd):
        p = self.__adb_open(cmd)
        while 1:
            line = p.stdout.readline()
            if not line:
                break

    def __shell(self, cmd):
        p = self.__shell_open(cmd)
        while 1:
            line = p.stdout.readline()
            if not line:
                break

    def wait_for_boot(self, interval=30, timeout=10):
        while 1:
            def y(x):
                if platform.system() == 'Windows':
                    x.terminate()
                else:
                    os.killpg(x.pid, signal.SIGUSR1)

            p = self.__adb_open('wait-for-device')
            if timeout > 0:
                t = threading.Timer(timeout, y, args=(p,))
                t.start()
            else:
                t = None
            p.wait()
            if t:
                if t.isAlive():
                    t.cancel()
                else:
                    return False

            if self.__shell_readline('getprop sys.boot_completed') == '1':
                break
            else:
                time.sleep(interval)
        return True

    def adb_open(self, cmd):
        self.wait_for_boot()
        return self.__adb_open(cmd)

    def shell_open(self, cmd):
        self.wait_for_boot()
        return self.__shell_open(cmd)

    def adb_readline(self, cmd):
        self.wait_for_boot()
        return self.__adb_readline(cmd)

    def shell_readline(self, cmd):
        self.wait_for_boot()
        return self.__shell_readline(cmd)

    def adb_readlines(self, cmd):
        self.wait_for_boot()
        return self.__adb_readlines(cmd)

    def shell_readlines(self, cmd):
        self.wait_for_boot()
        return self.__shell_readlines(cmd)

    def adb(self, cmd):
        self.wait_for_boot()
        self.__adb(cmd)

    def shell(self, cmd):
        self.wait_for_boot()
        self.__shell(cmd)

    def push(self, local, remote):
        self.adb('push "%s" %s' % (local, remote))

    def pull(self, remote, local):
        self.adb('pull %s "%s"' % (remote, local))

    def install(self, local):
        tmp_apk = '%s/tmp.apk' % DATA_LOCAL_TMP
        self.push(local, tmp_apk)
        sdk_int = int(get_prop(self, 'ro.build.version.sdk'))
        return self.shell_readlines('pm install %s "%s"' % ('-r' if sdk_int < 23 else '-r -g', tmp_apk))

    def uninstall(self, package):
        return self.shell_readlines('pm uninstall %s' % package)

    def reboot(self, interval=1, mode=''):
        self.adb('reboot %s' % mode if mode else 'reboot')
        if not mode:
            self.wait_for_boot(interval)

    def root(self):
        return self.adb_readline('root')

    def unroot(self):
        return self.adb_readline('unroot')

    def get_state(self):
        return self.__adb_readline('get-state')

    def get_serialno(self):
        return self.adb_readline('get-serialno')

    def remount(self):
        return self.adb_readlines('remount')

    def popen(self, cmd, timeout=0):
        # if timeout > 0:
        # cmd = 'timeout %d %s' % (timeout, cmd)
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)


class Device(dict):
    def __init__(self, serialno, product=None, model=None, device=None):
        super(Device, self).__init__(serialno=serialno, product=product, model=model, device=device)
