# -*- coding: utf-8 -*-
import adbkit
import os
import platform
import shutil
import tarfile
import time
from abc import ABCMeta, abstractmethod

DEBUG = platform.system() == 'Windows'
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_LOCAL_TMP = '/data/local/tmp'


class Executor(object):
    __metaclass__ = ABCMeta

    def __init__(self, adb, work_out):
        self.adb = adb
        self.work_out = work_out
        self.data_work_path = '%s/%s' % (DATA_LOCAL_TMP, self.id())
        self.work_dir = WORK_DIR

    @classmethod
    def id(cls):
        return cls.__module__.split('.')[-1].strip()

    def __kill_track(self):
        self.adb.shell('kill -9 {0}{1}/busybox pidof busybox{0}'.format('`' if DEBUG else '\\`', self.data_work_path))

    def track(self, data):
        pass

    def start(self, *args):
        self.shell(('start',) + args + ('>' if DEBUG else '\\>', '%s/nohup.txt' % self.data_work_path), True)

    def execute(self):
        print u'正在导入 %s 测试脚本' % self.id()
        self.import_script()
        self.__kill_track()
        print u'正在执行 %s 测试' % self.id()
        self.start()
        self.adb.shell('touch %s/track' % self.data_work_path)
        while 1:
            if self.adb.shell_readline('{0}/busybox tail -1 {0}/track'.format(self.data_work_path)) == 'done':
                break
            p = self.adb.shell_open('{0}/busybox tail -1 -F {0}/track'.format(self.data_work_path))
            while 1:
                line = p.stdout.readline()
                if not line or line.strip() == 'done':
                    break
                elif line.strip():
                    echo_to_file(self.adb, '', '%s/track' % self.data_work_path)
                    self.track(line.strip())
            p.terminate()
            self.__kill_track()
        print u'%s测试执行完成' % self.id()
        self.shell(('done',)).wait()
        print u'正在导出 %s 测试数据' % self.id()
        self.export_result()

        print u'生成 %s 报告' % self.id()
        self.parsers()

    def stop(self):
        # stop exec
        pass

    def shell(self, args, nohup=False):
        print 'shell====== ', args
        pattern = '{0}{1}/busybox nohup sh {1}/main.sh {2}{0}' if nohup else '{0}sh {1}/main.sh {2}{0}'
        return self.adb.shell_open(pattern.format('"' if DEBUG else '\\"', self.data_work_path, ' '.join(args)))

    def import_script(self):
        self.adb.shell('rm -rf %s' % self.data_work_path)
        self.adb.shell('mkdir -p %s' % self.data_work_path)
        self.adb.push(os.path.join(WORK_DIR, self.id()), DATA_LOCAL_TMP)
        self.adb.shell('chmod 755 %s/busybox' % self.data_work_path)

    def export_result(self):
        print 'export: ', self.work_out
        if not os.path.exists(self.work_out):
            os.makedirs(self.work_out)
            time.sleep(3)
        self.adb.shell('{0}/busybox tar -C {0} -zcvf {0}/out.tar.gz out'.format(self.data_work_path))
        tar_file_path = os.path.join(self.work_out, '%s.tar.gz' % self.id())
        print '%s/out.tar.gz' % self.data_work_path
        print 'tar_file_path: ', tar_file_path
        self.adb.pull('%s/out.tar.gz' % self.data_work_path, tar_file_path)
        if os.path.exists(tar_file_path):
            with tarfile.open(tar_file_path) as tar:
                for name in tar.getnames():
                    tar.extract(name, self.work_out)
            src_file_path = os.path.join(self.work_out, 'out')
            if os.path.exists(src_file_path):
                dst_file_path = os.path.join(self.work_out, self.id())
                shutil.rmtree(dst_file_path, True)
                os.rename(src_file_path, dst_file_path)

    def parsers(self):
        print 'parser test datas out put report'