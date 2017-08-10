# -*- coding: utf-8 -*-
import codecs
import copy
import csv
import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import xlwt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import adbkit

WORK_OUT = os.path.join(os.path.expanduser('~'), 'eebbk-results')
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import re


class ModuleMonitor():
    def __init__(self, adb, work_out, child):
        self.adb = adb
        self.work_out = work_out
        self.child = child

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

    def csv_to_xls(self, csv_file):
        print u'csv 转换为execel 带图表'
        block_process = {}  # 统计进程及卡顿次数
        xlsf = xlwt.Workbook(encoding='utf-8')
        sheet1 = xlsf.add_sheet(u'结果统计')
        sheet2 = xlsf.add_sheet(u'卡顿信息', cell_overwrite_ok=True)

        # Define the header and footer fonts
        header_font = xlwt.Font()
        header_font.bold = True
        header_font.colour_index = 0
        header_font.height = 300  # 字体大小

        normal_font = copy.copy(header_font)
        normal_font.name = 'Times New Roman'
        normal_font.height = 200  # 非标题
        normal_font.bold = False

        # 文本位置
        header_alignment = xlwt.Alignment()  # 创建居中
        header_alignment.horz = xlwt.Alignment.HORZ_CENTER  # 可取值: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        header_alignment.vert = xlwt.Alignment.VERT_CENTER  # 可取值: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED

        normal_alignment = xlwt.Alignment()  # 创建居中
        normal_alignment.horz = xlwt.Alignment.HORZ_LEFT  # 可取值: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        normal_alignment.vert = xlwt.Alignment.VERT_CENTER  # 可取值: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED

        # 背景色
        header_badBG = xlwt.Pattern()
        header_badBG.pattern = header_badBG.SOLID_PATTERN
        header_badBG.pattern_fore_colour = 170

        # 边界线
        borders = xlwt.Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1
        borders.bottom_colour = 0x3A

        header_style = xlwt.XFStyle()  # 创建样式

        normal_style_trace = xlwt.easyxf('align: wrap on')
        normal_style_trace.font = normal_font
        normal_style_trace.borders = borders

        normal_style = copy.copy(normal_style_trace)
        normal_style.alignment = normal_alignment

        # 背景色
        header_style.font = header_font
        header_style.alignment = header_alignment
        header_style.pattern = header_badBG
        header_style.borders = borders

        sheet2.col(0).width = 256 * 14
        sheet2.col(1).width = 256 * 14
        sheet2.col(2).width = 256 * 40
        sheet2.col(3).width = 256 * 14
        sheet2.col(4).width = 256 * 40
        sheet2.col(5).width = 256 * 80
        sheet2.col(6).width = 256 * 40

        # 标题行设置高度
        tall_style = xlwt.easyxf('font:height 720;')
        row0 = sheet2.row(0)
        row0.set_style(tall_style)

        csvfile = open(os.path.join(self.work_out, csv_file + '.csv'), "rb")
        reader = csv.reader(csvfile)
        l = 0
        for line in reader:
            r = 0
            for i in line:
                if l == 0:
                    sheet2.write(0, r, i, header_style)  # 标题行
                else:
                    if r == 2:
                        block_process[i] = block_process.get(i, 0) + 1  # 统计进程名字和出现卡顿的次数
                    if r == 5:  # tracestack 自动换行
                        sheet2.write(l, r, i, normal_style_trace)
                    else:
                        sheet2.write(l, r, i, normal_style)
                r = r + 1
            l = l + 1

        l = 1
        sheet1.write(0, 0, u'进程', header_style)
        sheet1.write(0, 1, u'卡顿次数', header_style)
        sheet1.col(0).width = 256 * 40
        sheet1.col(1).width = 256 * 14
        for value in sorted(block_process.items(), key=lambda item: item[1], reverse=True):
            sheet1.write(l, 0, value[0], normal_style)
            sheet1.write(l, 1, value[1], normal_style)
            l += 1

        excel_filename = str(csv_file.split(".")[0]) + ".xls"
        xlsf.save(os.path.join(self.work_out, excel_filename))
        plt.subplots()
        index = np.arange(len(block_process.keys()))
        plt.barh(index, tuple([test[1] for test in sorted(block_process.items(), key=lambda item: item[1])]),
                 label='times')
        plt.ylabel(u'进程名称', fontproperties='SimHei')
        plt.xlabel(u'卡顿次数(单位:次)', fontproperties='SimHei')
        plt.title(u'性能监控统计', fontproperties='SimHei')
        for a, b in zip(index, tuple([test[1] for test in sorted(block_process.items(), key=lambda item: item[1])])):
            plt.text(b + 0.2, a, '%.0f' % b, ha='center', va='bottom', fontsize=7)
        plt.yticks(index, tuple([test[0] for test in sorted(block_process.items(), key=lambda item: item[1])]))
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.work_out, str(csv_file.split(".")[0]) + ".jpg"))

    def execute(self):
        print u'执行卡顿监控测试'

    def setup(self):
        check = QCheckBox(u'继续上一次的Monkey测试')
        check.toggled[bool].connect(self.retryChecked)

        self.radio1 = QRadioButton(u'整机Monkey测试')
        self.radio1.toggled[bool].connect(self.radio1Toggled)
        self.radio3 = QRadioButton(u'整机Monkey测试(安装top50应用且可测第三方应用)')
        self.radio3.setChecked(self.install)
        self.radio3.toggled[bool].connect(self.radio3Toggled)
        self.radio2 = QRadioButton(u'单包Monkey测试')
        self.radio2.setChecked(self.single)
        self.radio2.toggled[bool].connect(self.radio2Toggled)
        self.edit1 = QLineEdit(str(self.seed))
        self.edit1.setValidator(QIntValidator())
        self.edit1.textChanged[str].connect(self.edit1Changed)
        self.edit2 = QLineEdit(str(self.throttle))
        self.edit2.setValidator(QIntValidator())
        self.edit2.textChanged[str].connect(self.edit2Changed)
        self.edit3 = QLineEdit(str(self.count))
        self.edit3.setValidator(QIntValidator())
        self.edit3.textChanged[str].connect(self.edit3Changed)
        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(u'种子数'), 0, 0)
        gridLayout.addWidget(self.edit1, 0, 1)
        gridLayout.addWidget(QLabel(u'事件间隔'), 1, 0)
        gridLayout.addWidget(self.edit2, 1, 1)
        gridLayout.addWidget(QLabel(u'事件次数'), 2, 0)
        gridLayout.addWidget(self.edit3, 2, 1)
        itemLayout = QVBoxLayout()
        itemLayout.addWidget(self.radio1)
        itemLayout.addWidget(self.radio3)
        itemLayout.addWidget(self.radio2)

        itemLayout.addStretch()
        itemLayout.addLayout(gridLayout)
        self.itemGroup = QGroupBox(u'Monkey测试参数')
        self.itemGroup.setLayout(itemLayout)
        selall = QListWidgetItem(u'全选')
        selall.setCheckState(Qt.Checked)
        selall.setData(1, QVariant('selall'))
        self.list = QListWidget()
        self.list.itemChanged.connect(self.itemChanged)
        self.list.addItem(selall)
        for key in self.temppkgs.keys():
            item = QListWidgetItem(key)
            item.setCheckState(Qt.Checked)
            item.setData(1, QVariant(key))
            self.list.addItem(item)
        listLayout = QVBoxLayout()
        listLayout.addWidget(self.list)
        self.listGroup = QGroupBox(u'单包Monkey测试可选包名')
        self.listGroup.setLayout(listLayout)

        itemLayout = QHBoxLayout()
        itemLayout.addWidget(self.itemGroup)
        itemLayout.addWidget(self.listGroup)
        itemLayout.setStretch(0, 1)
        itemLayout.setStretch(1, 3)
        layout = QVBoxLayout()
        layout.addWidget(check)
        layout.addLayout(itemLayout)


if __name__ == "__main__":
    threads = []
    all_connect_devices = adbkit.devices()
    for device in all_connect_devices:
        if device['serialno'] in sys.argv:
            adb = adbkit.Adb(device)
            ModuleMonitor(adb, sys.argv[2]).parsers()
