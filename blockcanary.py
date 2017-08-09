# -*- coding: utf-8 -*-
import codecs
import copy
import csv
import glob
import os
import xlsxwriter
import xlwt

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
        # self.csv_generate(data, 'temp')
        # # self.execel_generate(data, str(os.getpid()))
        # self.csv_to_xls('temp')

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
        for key, value in block_process.items():
            sheet1.write(l, 0, key, normal_style)
            sheet1.write(l, 1, value, normal_style)
            l += 1

        workbook = xlsxwriter.Workbook('chart.xlsx')
        worksheet = workbook.add_worksheet()

        chart = workbook.add_chart({'type': 'bar'})
        # Configure the chart. In simplest case we add one or more data series.
        chart.add_series(
            {'values': '=Sheet1!$B$2:$B$5', 'categories': '=Sheet1!$A$2:$A$5', 'data_labels': {'value': True}})

        # Insert the chart into the worksheet.
        worksheet.insert_chart('F7', chart)


        excel_filename = str(csv_file.split(".")[0]) + ".xls"
        xlsf.save(os.path.join(self.work_out, excel_filename))


if __name__ == "__main__":
    block_process = {'pkg1': 1, 'pkg2': 4}
