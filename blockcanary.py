# -*- coding: utf-8 -*-
import codecs
import csv
import glob
import os
import sys

import xlwt

import adbkit

WORK_OUT = os.path.join(os.path.expanduser('~'), 'eebbk-results')
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import re


class ModuleMonitor():
    def __init__(self, adb, work_out):
        self.adb = adb
        self.work_out = work_out

    @classmethod
    def id(cls):
        return cls.__module__.split('.')[-1].strip()

    def title(self):
        return u'验证AndroidPerformanceMonitor工具'

    def desc(self):
        return u'应用埋点监控数据;测试模拟用户操作产生数据并解析生成报告并上报。'

    def parsers(self):
        print u'AndroidPerformanceMonitor监控应用UI主线程卡顿情况'
        work_dir = os.path.join(self.work_out, 'blockcanary')
        logs = glob.iglob(os.path.join(work_dir, '*.log'))
        data = {}
        for log in logs:
            if os.path.exists(log):
                key = os.path.basename(log)
                value = {'serialno': 'serialno', 'model': u'机型', 'process': u'进程名', 'stacktrace': u'堆栈信息',
                         'versionname': u'版本号', 'others': u'其它待解析信息'}
                with open(log, 'r') as f:
                    tracenum = 0
                    for line in f:
                        m = re.search('versionName = (.*)', line)
                        if m:
                            versionName = m.groups()[0]
                            value['versionname'] = versionName
                            print versionName
                            continue
                        m = re.search('model = (.*)', line)
                        if m:
                            model = m.groups()[0]
                            print model
                            value['model'] = model
                            continue
                        m = re.search('process = (.*)', line)
                        if m:
                            process = m.groups()[0]
                            print process
                            value['process'] = process
                            continue
                        m = re.search('time-start = (.*)', line)
                        if m:
                            timestart = m.groups()[0]
                            print timestart
                            print 'timestart '
                            value['timestart'] = timestart
                            continue
                        if line.startswith('stack'):
                            m = re.search('stack = (.*)', line)
                            if m:
                                stack = m.groups()[0]
                                value['stacktrace'] = line
                                print stack
                                tracenum += 1
                                continue
                        if 1 <= tracenum <= 50:
                            tracenum += 1
                            value['stacktrace'] += line
                    data[key] = value
                    f.close()
        self.csv_generate(data, str(os.getpid()))
        # self.execel_generate(data, str(os.getpid()))
        self.csv_to_xls(str(os.getpid()))

    def csv_generate(self, data, filename):
        csvfile = file(os.path.join(self.work_out, filename + '.csv'), 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['机型', '序列号', '进程名称', '版本号', '开始时间', '堆栈信息', 'log文件'])
        for key, value in data.items():
            writer.writerow(
                [value['model'], value['serialno'], value['process'], value['versionname'], str(value['timestart']),
                 value['stacktrace'], key])
        csvfile.close()

    # def execel_generate(self, data, filename):
    #     print u'生成execel文件'



    def csv_to_xls(self, csv_file):
        print u'csv 转换为execel 带图表'
        xlsf = xlwt.Workbook(encoding='utf-8')
        sheet1 = xlsf.add_sheet(u'结果统计')
        sheet2 = xlsf.add_sheet(u'卡顿信息')

        # sheet = xlsf.add_sheet(u'格式设置')
        alignment = xlwt.Alignment()  # 创建居中
        alignment.horz = xlwt.Alignment.HORZ_CENTER  # 可取值: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        alignment.vert = xlwt.Alignment.VERT_CENTER  # 可取值: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
        badBG = xlwt.Pattern()
        badBG.pattern = badBG.SOLID_PATTERN
        badBG.pattern_fore_colour = 1

        style0 = xlwt.XFStyle()  # 创建样式
        style0.alignment = alignment  # 给样式添加文字居中属性
        style0.font.height = 200  # 设置字体大小
        style0.pattern = badBG
        # # ----------设置列宽高--------------
        col1 = sheet2.col(0)  # 获取第0列
        col1.width = 100 * 400  # 设置第0列的宽为380，高为20

        styleBlueBkg = xlwt.easyxf('pattern: pattern solid, fore_colour ocean_blue; font: bold on;')
        # # ----------合并单元格-----------
        # sheet.write_merge(4, 6, 0, 1, '测试合并行和列数据', style)  # 合并第4到6行的0列和第1列，并将样式添加进去，注意：excel的行和列都是从0开始
        # sheet.write(0, 0, '姓名', style)  # 给第0行的第0列插入值，并添加样式
        # sheet.write(0, 1, '年龄', style)  # 给第0行的第1列插入值，并添加样式
        # sheet.write(0, 2, '性别', style)  # 给第0行的第2列插入值，并添加样式
        # # 创建一个测试数据列表
        # stu_list = [{}, {"name": "张三", "age": 23, "gender": "男"}, {"name": "李四", "age": 22, "gender": "男"},
        #             {"name": "王五", "age": 25, "gender": "男"}]
        # # 循环插入值
        # for index, x in enumerate(stu_list):
        #     if index != 0:
        #         sheet.write(index, 0, x["name"], style)
        #         sheet.write(index, 1, x["age"], style)
        #         sheet.write(index, 2, x["gender"], style)
        # xlsf.save('demo1.xls')


        # csvfile = file(os.path.join(self.work_out, csv_file + '.csv'), 'wb')
        print self.work_out
        csvfile = open(os.path.join(self.work_out, csv_file + '.csv'), "rb")
        print os.path.join(self.work_out, csv_file + '.csv')
        reader = csv.reader(csvfile)
        l = 0
        for line in reader:  # line  行
            r = 0  # 列
            for i in line:
                sheet2.write(l, r, i, style0)
                r = r + 1
            l = l + 1
        excel_filename = str(csv_file.split(".")[0]) + ".xls"
        xlsf.save(os.path.join(self.work_out, excel_filename))


if __name__ == "__main__":
    print sys.argv[1]
    threads = []
    all_connect_devices = adbkit.devices()
    for device in all_connect_devices:
        if device['serialno'] in sys.argv:
            adb = adbkit.Adb(device)
            ModuleMonitor(adb, sys.argv[2]).parsers()
