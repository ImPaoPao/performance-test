# -*- coding: utf-8 -*-
import codecs
import csv
import datetime
import os
import platform
import re
from runner import Executor

WORK_OUT = os.path.join(os.path.expanduser('~'), 'eebbk-results')
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def get_exetime(starttime, endtime):
    exetime = 0
    list1 = starttime.split('.')
    list2 = endtime.split('.')
    starttime_sec = list1[0]
    starttime_minsec = '0.' + list1[1]
    endtime_sec = list2[0]
    endtime_minsec = '0.' + list2[1]
    time1 = datetime.datetime.strptime(starttime_sec, "%m-%d %H:%M:%S")
    time2 = datetime.datetime.strptime(endtime_sec, "%m-%d %H:%M:%S")
    if time2 > time1:
        temp = time2 - time1
        exetime = temp.total_seconds() + float(endtime_minsec) - float(starttime_minsec)
    if time2 == time1:
        if endtime_minsec > starttime_minsec:
            exetime = float(endtime_minsec) - float(starttime_minsec)
    return exetime


class LauncherModule(Executor):
    def __init__(self, adb, work_out):
        super(LauncherModule, self).__init__(adb, work_out)

    def parsers(self):
        print u'应用内部切换时间解析'
        print 'parsers app module'
        print self.work_out
        dir_dict = {}
        work_dir = os.path.join(self.work_out, 'module')
        for root, dirs, files in os.walk(work_dir):
            for name in files:
                if name == 'log.txt':
                    log = os.path.join(root, 'log.txt')
                    result = os.path.join(root, 'result.xml')
                    if os.path.exists(log) and os.path.exists(result):
                        dir_dict[os.path.basename(root)] = {'log': log, 'result': result}
        data = self.parser_files(dir_dict)
        self.csv_generate(data, self.id())

    def parser_files(self, file_dict):
        data_time = {}
        data_displayed = {}
        for key, values in file_dict.items():
            print u'用例：', key
            log = values['log']
            result = values['result']
            try:
                tree = ET.parse(result)
                root = tree.getroot()
            except Exception as e:
                print(u'读取xml文件异常')
            else:
                start_rule = '(\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}\.\d{3}).*\s*ActivityManager: START'
                end_rule = '(\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}\.\d{3}).*\s*ActivityManager: Displayed (.*)/(.*):'
                window_animation_rule = '(\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}\.\d{3}).*\s*WindowManager: Eval win Window(.*)isDrawn=true, isAnimationSet=false'
                segments = root.findall('Segment')
                data_time[key] = [[], [], [], [],[],[],[],[]]
                for segment in segments:
                    segment_list = []
                    window_time = ''
                    starttime = segment.get('starttime')
                    endtime = segment.get('endtime')
                    stoptime = segment.get('loadtime')
                    startScreen = segment.get('startScreen')
                    endScreen = segment.get('endScreen')
                    compareScreen = segment.get('compareTime')
                    compareResult = segment.get('compareResult')
                    with open(log, 'r') as flog:
                        for line in flog:
                            m = re.search(start_rule, line)
                            n = re.search(end_rule, line)
                            animation = re.search(window_animation_rule, line)
                            if m or n or animation:
                                if m:
                                    line_time = m.groups()[0]
                                if n:
                                    line_time = n.groups()[0]
                                    # displayed_activity = n.groups()[2] if len(m.groups()) > 2 else None
                                if animation:
                                    time_tmp = animation.groups()[0]
                                    if time_tmp <= endtime and time_tmp >= starttime:
                                        window_time = time_tmp
                                        print window_time
                                if (line_time <= endtime and line_time >= starttime):
                                    segment_list.append(line_time)

                        flog.close()
                    print u'执行时间:'
                    print segment_list
                    print 'window time:', window_time
                    print 'end time:', endtime
                    print 'stoptime:', stoptime
                    if segment_list:
                        icon_time = get_exetime(starttime, segment_list[0])
                        exe_time = get_exetime(segment_list[0], segment_list[-1])
                        screen_time = get_exetime(startScreen, endScreen)
                        compare_time = get_exetime(endScreen, compareScreen)
                        data_time[key][0].append(icon_time)
                        data_time[key][1].append(exe_time)
                        data_time[key][2].append(screen_time)
                        data_time[key][3].append(compare_time)
                        data_time[key][4].append(compareResult)
                        print exe_time
                        if stoptime and stoptime >= segment_list[-1]:
                            display_stop = get_exetime(segment_list[-1], stoptime)
                            data_time[key][5].append(display_stop)
                            print 'display_stop:', display_stop
                        if window_time != '' and window_time > segment_list[-1]:
                            display_window = get_exetime(segment_list[-1], window_time)
                            data_time[key][6].append(display_window)
                            print 'display_window', display_window
                        print '========================='

        return data_time

    def csv_generate(self, data, filename):
        csvfile = file(filename + '.csv', 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['应用名称', '平均值', '第一次', '第二次', '第三次'])
        for key, value in data.items():
            display_window = value[6]
            display_stop = value[5]
            exetime = value[1]
            icontime = value[0]
            screentime = value[2]
            comparetime = value[3]
            compareresult = value[4]
            writer.writerow([key])
            if icontime:
                writer.writerow(['点击图标'] + [sum(icontime) / (len(icontime) if icontime else 1)] + icontime)
            if exetime:
                writer.writerow(['加载(start-displayed)'] + [sum(exetime) / (len(exetime) if exetime else 1)] + exetime)
            if screentime:
                writer.writerow(['截屏'] + [sum(screentime) / (len(screentime) if screentime else 1)] + screentime)
            if comparetime:
                writer.writerow(['图片对比'] + [sum(comparetime) / (len(comparetime) if comparetime else 1)] + comparetime)
            if compareresult:
                writer.writerow(
                    ['图片匹配度'] + [0]+ compareresult)
            if display_stop:
                writer.writerow(['displayed-动画显示完成'] + [sum(display_stop) / (len(display_stop) if display_stop else 1)] + display_stop)
            if display_window:
                writer.writerow(
                    ['displayed-windows窗口动画播放完成'] + [sum(display_window) / (len(display_window) if display_window else 1)] + display_window)

        csvfile.close()
