# -*- coding: utf-8 -*-
import codecs
import csv
import datetime
import os
import platform
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')
from runner import Executor

WORK_OUT = os.path.join(os.path.expanduser('~'), 'eebbk-results')
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

dict1 = {'launchRecentMemory': '剩余内存'}


class FreeMemory(Executor):
    def __init__(self, adb, work_out):
        super(FreeMemory, self).__init__(adb, work_out)

    def parsers(self):
        print u'剩余内存'
        print self.work_out
        dir_dict = {}
        work_dir = os.path.join(self.work_out, 'freememory')
        for root, dirs, files in os.walk(work_dir):
            for name in files:
                if name == 'result.xml':
                    result = os.path.join(root, 'result.xml')
                    if os.path.exists(result):
                        dir_dict[os.path.basename(root)] = result
        data = self.parser_files(dir_dict)
        print 'before csv'
        self.csv_generate(data, self.id())
        print data

    def parser_files(self, file_dict):
        data = {}
        for key, value in file_dict.items():
            print u'用例：', key
            result = value
            try:
                tree = ET.parse(result)
                root = tree.getroot()
            except Exception as e:
                print(u'读取xml文件异常')
            else:
                segments = root.findall('Segment')
                data[key] = []
                for segment in segments:
                    memory = segment.get('memory')
                    if '/' in memory:
                        data[key].append(memory.split('/')[0])
        return data

    def csv_generate(self, data, filename):
        csvfile = file(os.path.join(self.work_out, filename + '.csv'), 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['ID', '用例名称', '用例描述', '第一次', '第二次', '第三次', '平均值'])
        for key, value in data.items():
            memory = value
            writer.writerow([key, dict1[key] if key in dict1 else key, dict1[key] if key in dict1 else key])
            sum = 0
            for item in memory:
                if item:
                    sum += float(item.split(' ')[0].strip())
            avg = sum / len(memory)
            print avg
            print memory
            writer.writerow(['', '', ''] + memory + [avg])
        csvfile.close()
