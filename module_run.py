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

dict1 = {'launchEnglishTalk': '英语听说', 'launchSyncChinese': '同步语文', 'launchBbkMiddleMarket': '应用商店',
         'launchSynMath': '同步数学', 'launchOneSearch': '一键搜', 'launchQuestionDatabase': '好题精练',
         'launchSyncEnglish': '同步英语', 'launchVision': '视力保护', 'launchVtraining': '名师辅导',
         'showSynMathBook': '同步数学:点击书本→书本目录加载完成', 'addMathBook': '同步数学:点击添加按钮→下载界面加载完成',
         'changeSynMathBook': '同步数学:进入课本目录界面，点击左边换书按钮→书架界面显示完成',
         'showExplanationSynMathContent': '同步数学:进入课本目录界面，点击动画讲解→动画讲解界面加载完成',
         'downloadExplanatinSynMathContent': '同步数学:进入课本目录界面，点击动画讲解右边的下载按钮→下载页面加载完成',
         'showDetailsSynMathBook': '同步数学:点击教辅目录→进入课本详情',
         'refreshSynMath': '同步数学:书架界面10本书，点击刷新→刷新完成',
         'showExplanationSynMathBook': '同步数学:书本内容界面，点击左上角目录按钮，点击知识讲解→知识讲解内容加载完成',
         'synEnglishRefresh': '同步英语:书架界面10本书，点击刷新→刷新完成',
         'addSyncEnglishBook': '同步英语:点击添加按钮→下载界面加载完成',
         'showSyncEnglishBook': '同步英语:点击书本→书本内容界面显示完成',
         'syncEnglishSelfInfo': '同步英语:书本内容界面点击头像→个人信息页面加载完成',
         'syncEnglishFunTest': '同步英语:书本内容界面点击趣味测验→测验页面内容加载完成',
         'syncEnglishFlash': '同步英语:书本内容界面点击flash按钮→flash页面加载完成',
         'syncEnglishAccessDict': '同步英语:点读页面，点击句子选择单词--查，点击反查→词典列表弹出框加载完成',
         'syncEnglishOlaAccessBbkMarket': '同步英语:趣味测验点击欧拉学英语→跳转到商店页面加载完成',
         'addChineseBook': '同步语文:添加按钮->界面加载完成',
         'showSynChineseBook': '同步语文:点击书本→书本内容界面显示完成',
         'showDetailsSynChineseBook': '同步语文:点击教辅目录→进入课本详情',
         'syncChineseAccessDict': '同步语文:点击查字词→调转到词典界面',
         'synChineseSelfInfo': '同步语文:书本内容界面点击头像→个人信息页面加载完成',
         'synChineseNewWord': '同步语文:生字页面，点击一个生字，点击写一写→进入写一写界面',
         'synChineseRefresh': '同步语文:书架界面10本书，点击刷新→刷新完成'
         }


def get_exetime(starttime, endtime):
    exetime = 0
    if starttime and endtime:
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





def parsers(work_out):
    print u'应用内部切换时间解析'
    print 'parsers app module'

    dir_dict = {}
    work_dir = os.path.join(work_out, 'module')
    for root, dirs, files in os.walk(work_dir):
        for name in files:
            if name == 'result.xml':
                result = os.path.join(root, 'result.xml')
                if os.path.exists(result):
                    dir_dict[os.path.basename(root)] = result
    data = parser_files(dir_dict)
    csv_generate(data, "module")

def parser_files(file_dict):
    data_time = {}
    data_displayed = {}
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
            data_time[key] = [[], [], [], [], []]
            for segment in segments:
                starttime = segment.get('starttime')
                endtime = segment.get('endtime')
                loadtime = segment.get('loadtime')
                refreshtime = segment.get('refreshtime')
                loadresult = segment.get('loadresult')
                refreshresult = segment.get('refreshresult')
                exe_time = get_exetime(starttime, loadtime)
                rexe_time = get_exetime(starttime, refreshtime)
                run_time = get_exetime(starttime, endtime)
                data_time[key][0].append(exe_time)
                data_time[key][1].append(rexe_time)
                data_time[key][2].append(loadresult)
                data_time[key][3].append(refreshresult)
                data_time[key][4].append(run_time)
    return data_time

def csv_generate(data, filename):
    csvfile = file(filename + '.csv', 'wb')
    csvfile.write(codecs.BOM_UTF8)
    writer = csv.writer(csvfile, dialect='excel')
    writer.writerow(['应用名称', '第一次', '第二次', '第三次', '第四次', '第五次', '第六次', '第七次', '第八次', '第九次', '第十次', '平均值'])
    for key, value in data.items():
        exetime = value[0]
        rexetime = value[1]
        loadresult = value[2]
        refreshresult = value[3]
        runtime = value[4]
        writer.writerow([dict1[key] if key in dict1 else key])
        if exetime:
            writer.writerow(['点击-页面出现'] + exetime + [sum(exetime) / (len(exetime) if exetime else 1)])
        if rexetime:
            writer.writerow(
                ['点击-页面内容加载完'] + rexetime + [sum(rexetime) / (len(rexetime) if rexetime else 1)])
        if loadresult:
            writer.writerow(['匹配度'] + [0] + loadresult)
        if refreshresult:
            writer.writerow(['匹配度'] + [0] + refreshresult)
            # if runtime:
            #     writer.writerow(['t'] + [sum(runtime) / (len(runtime) if runtime else 1)] + runtime)
    csvfile.close()
if __name__ == "__main__":
    print "fffffffffffffff"
    work_out=r"C:\Users\admin\eebbk-results\S1730016BL\2017-05-28-18-25-14"
    parsers(work_out)
