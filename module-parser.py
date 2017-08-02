# -*- coding: utf-8 -*-
import codecs
import copy
import csv
import datetime
import os
import sys
import time
from collections import OrderedDict

import adbkit

WORK_OUT = os.path.join(os.path.expanduser('~'), 'eebbk-results')
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

dict1 = {'launchEnglishTalk': '英语听说', 'launchSynChinese': '同步语文', 'launchBbkMiddleMarket': '应用商店',
         'launchSynStudy': '学科同步',
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
         'synChineseRefresh': '同步语文:书架界面10本书，点击刷新→刷新完成',
         'showEtPlayUi': '选择教材添加后，点击教材目录→进入播放界面',
         'showEtPlayAudioContent': '播放界面，点击右下角目录按钮→目录加载完成',
         'showEtPlayAudio': '播放界面，点击目录按钮中任意目录→播放内容加载完成',
         'showEtRanking': '点击我的排行→排行榜加载完成',
         'showBbkMAppDetails': '首页点击应用→应用详情加载完成',
         'showBbkMClassCh': '分类页面，点击语文→内容加载完成',
         'showBbkMSelfInfo': '个人中心未登录，点击头像→个人中心页面加载完成',
         'showBbkMCopyright': '点击版权声明→页面加载完成',
         'showBbkMDownloadList': '下载10个应用，点击下载中心→下载列表加载完成',
         'showVisionSettings': '点击设置按钮→显示设置界面',
         'showVisionProtection': '点击护眼小知识→显示不严小知识界面',
         'showQdExample': '点击智能练习目录→题目加载完成',
         'showQdExamExplanation': '点击例题讲解目录→题目加载完成',
         'showQdRealExamList': '点击真题密卷科目→真题目录界面加载完成',
         'showQdRealExamContent': '点击真题目录界面目录→题目加载完成',
         'showQdRanking': '点击排行榜→排行榜页面加载完成',
         'showVtCourseTeacher': '选课界面，点击banner图名师在这里图片→名师页面加载完成',
         'showVtTeacherInfo': '点击名师头像→名师详情加载完成',
         'showVtRanking': '我的界面，点击排行榜→排行榜页面，加载完成',
         'showVtJoinCourse': '已加入5个课程，进入我的界面，点击已加入课程→列表内容加载完成',
         'showVtDownloadCourse': '已下载5个课程，进入我的界面，点击已下载课程→列表内容加载完成',
         'showVtCourse': '点击选课→科目→课程包封面，加载完成',
         'showVtMoreList': '点击首页更多精彩→课程列表页面，加载完成'
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


def run(adb, serialno, type):
    work_out = os.path.join(WORK_OUT, str(serialno), time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))
    LauncherModule(adb, work_out).execute()


class LauncherModule():
    def __init__(self, adb, work_out):
        self.adb = adb
        self.work_out = work_out

    @classmethod
    def id(cls):
        return cls.__module__.split('.')[-1].strip()

    def title(self):
        pass

    def desc(self):
        pass

    def parsers(self):
        print u'应用内部切换时间解析'
        dir_dict = {}
        work_dir = os.path.join(self.work_out, 'module')
        for root, dirs, files in os.walk(work_dir):
            for name in files:
                if name == 'result.xml':
                    result = os.path.join(root, 'result.xml')
                    if os.path.exists(result):
                        dir_dict[os.path.basename(root)] = result
                    break
                if name == 'instrument.txt':
                    result = os.path.join(root, 'instrument.txt')
                    if os.path.exists(result) and os.path.basename(root) not in dir_dict.keys():
                        dir_dict[os.path.basename(root)] = ''
        data = self.parser_files(dir_dict)
        self.csv_generate(data, 'temp')

    def parser_files(self, file_dict):
        data = {}
        for key, value in file_dict.items():
            print u'用例：', key, value
            result = value
            data[key] = {'exetime': [], 'rexetime': [], 'runtime': [], 'refreshresult': [], 'memory': [],
                         'loadresult': [], 'errortime': []}
            if not os.path.exists(result):
                data[key] = {'exetime': [0], 'rexetime': [0], 'runtime': [0], 'refreshresult': [0], 'memory': [0],
                             'loadresult': [0], 'errortime': [0]}
                print 'not result '
                continue
            try:
                tree = ET.parse(result)
                root = tree.getroot()
            except Exception as e:
                print(u'读取xml文件异常')
                data[key] = {'exetime': [0], 'rexetime': [0], 'runtime': [0], 'refreshresult': [0], 'memory': [0],
                             'loadresult': [0], 'errortime': [0]}
                print 'xml xceprion '
                continue
            else:
                print 'else==='
                segments = root.findall('Segment')
                if len(segments) < 1:
                    data[key] = {'exetime': [0], 'rexetime': [0], 'runtime': [0], 'refreshresult': [0], 'memory': [0],
                                 'loadresult': [0], 'errortime': [0]}
                    continue
                for segment in segments:
                    memory = segment.get('memory')
                    if memory != None:
                        if '/' in memory:
                            data[key]['memory'].append(memory.split('/')[0])
                    else:
                        starttime = segment.get('starttime')
                        endtime = segment.get('endtime')
                        loadtime = segment.get('loadtime')
                        lasttime = segment.get('lasttime')
                        refreshtime = segment.get('refreshtime')
                        loadresult = segment.get('loadresult')
                        refreshresult = segment.get('refreshresult')
                        if lasttime is not '':
                            temptime = get_exetime(starttime, lasttime)
                            error_time = get_exetime(lasttime, loadtime)
                        else:
                            temptime = get_exetime(starttime, loadtime)
                            error_time = 0
                        # 两张误差较小时
                        print error_time
                        if 0 < error_time * 1000 < 100:
                            # 截图时间比较小的 针对类似S1S H9S这种 前一张匹配度很小时取倒数第二次的时间。
                            print u'时间差比较小的........'
                            if int(loadresult) < 5:
                                print u'小于5'
                                if key == 'launchVision':
                                    print u'视力保护'
                                    exe_time = temptime
                                    rexe_time = get_exetime(starttime, refreshtime) - error_time
                                    data[key]['errortime'].append(error_time)
                                else:
                                    print 'else=: ',key
                                    exe_time = temptime - error_time
                                    rexe_time = get_exetime(starttime, refreshtime) - 2 * error_time
                                    data[key]['errortime'].append(error_time)
                            elif int(loadresult) <= 10:
                            # else :
                                print u'大于5'
                                exe_time = temptime-error_time/2
                                rexe_time = get_exetime(starttime, refreshtime) - error_time*3/2
                                data[key]['errortime'].append(error_time)
                            else:
                                exe_time = temptime
                                rexe_time = get_exetime(starttime, refreshtime) - error_time
                                data[key]['errortime'].append(error_time)
                        else:
                            print u'误差大的......'
                            # 适配S3类似截图时差比较大的
                            if int(loadresult) <= 5:
                                print u'小于5'
                                if key == 'launchVision':
                                    print u'视力保护'
                                    exe_time = temptime + error_time * 1 / 4
                                    rexe_time = get_exetime(starttime, refreshtime) - error_time*3 / 4
                                    data[key]['errortime'].append(error_time)
                                else:
                                    exe_time = temptime
                                    rexe_time = get_exetime(starttime, refreshtime) - error_time
                                    data[key]['errortime'].append(error_time)
                            elif int(loadresult) <= 10:
                                print u'小于等于10'
                                # if key == 'launchVision':
                                #     print u'视力保护'
                                exe_time = temptime + error_time / 2
                                rexe_time = get_exetime(starttime, refreshtime) - error_time / 2
                                data[key]['errortime'].append(error_time)
                                # else:
                                #     exe_time = temptime + error_time / 4
                                #     rexe_time = get_exetime(starttime, refreshtime) - error_time * 3 / 4
                                #     # exe_time = temptime + error_time*3 / 8
                                #     # rexe_time = get_exetime(starttime, refreshtime) - error_time *5/8
                                #     data[key]['errortime'].append(error_time)
                            else:
                                print u'大于10'
                                # if key == 'launchVision':
                                #     print u'视力保护'
                                exe_time = temptime + error_time * 3 / 4
                                rexe_time = get_exetime(starttime, refreshtime) - error_time / 4
                                data[key]['errortime'].append(error_time)
                                # else:
                                #     exe_time = temptime + error_time / 2
                                #     rexe_time = get_exetime(starttime, refreshtime) - error_time / 2
                                #     data[key]['errortime'].append(error_time / 2)
                                # if int(loadresult) < 10:
                                #     if key == 'launchVision':
                                #         exe_time = temptime + error_time / 2
                                #         rexe_time = get_exetime(starttime, refreshtime) - error_time / 2
                                #         data[key]['errortime'].append(error_time / 2)
                                #     else:
                                #         exe_time = temptime + error_time / 4
                                #         rexe_time = get_exetime(starttime, refreshtime) - error_time * 3 / 4
                                #         data[key]['errortime'].append(error_time)
                                # else:
                                #     exe_time = temptime + error_time / 2
                                #     rexe_time = get_exetime(starttime, refreshtime) - error_time / 2
                                #     data[key]['errortime'].append(error_time / 2)
                        run_time = get_exetime(starttime, endtime)
                        data[key]['exetime'].append(exe_time)
                        data[key]['rexetime'].append(rexe_time)
                        data[key]['loadresult'].append(loadresult)
                        data[key]['refreshresult'].append(refreshresult)
                        data[key]['runtime'].append(run_time)
        return data

    def csv_generate(self, data, filename):
        csvfile = file(os.path.join(self.work_out, filename + '.csv'), 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(
            ['ID', '模块', '应用名称', '测试项目', '第一次', '第二次', '第三次', '第四次', '第五次', '第六次', '第七次', '第八次', '第九次', '第十次', '平均值'])
        # for key, value in data.items():
        #     # 启动时间
        #     exetime = value['exetime']
        #     rexetime = value['rexetime']
        #     errortime = value['errortime']
        #     loadresult = value['loadresult']
        #     if exetime:
        #         writer.writerow([key, dict1[key], '点击-页面出现'] + exetime + [
        #             sum(exetime) / (len(exetime) if exetime else 1)])
        #     if rexetime:
        #         writer.writerow(
        #             ['', '', '点击-页面内容加载完'] + rexetime + [sum(rexetime) / (len(rexetime) if rexetime else 1)])
        #     if errortime:
        #         writer.writerow(
        #             ['', '', '最大可能误差'] + errortime + [sum(errortime) / (len(errortime) if errortime else 1)])
        #     # if loadresult:
        #     #     writer.writerow(['', '', '上一次匹配度'] + loadresult)
        #
        #     # 可用内存
        #     memory = value['memory']
        #     if memory:
        #         add = 0
        #         for item in memory:
        #             if item:
        #                 add += float(item.split(' ')[0].strip())
        #         avg = add / len(memory)
        #         print avg
        #         print memory
        #         writer.writerow(['', ''] + memory + [avg])
        # csvfile.close()
        # if self.module_start:
        #     cases = self.usedcases
        # else:
        #     cases = self.mousedcases

        mfile = os.path.join(r'D:\bbk-test-center\performance-test', 'testcase.ini')
        mofile = os.path.join(r'D:\bbk-test-center\performance-test', 'modulecase.txt')
        self.mocases = OrderedDict()
        self.cases = OrderedDict()
        self.usedcases = OrderedDict()
        self.mousedcases = OrderedDict()
        if os.path.exists(mfile):
            with open(mfile, 'rb') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    line = line.strip('')
                    list = line.split(' ')
                    clsname = list[0]
                    metname = list[1]
                    pkg = list[2]
                    label = list[3]
                    # if pkg in self.temppkgs.keys():
                    self.usedcases[metname] = {'label': label, 'pkg': pkg, 'clsname': clsname}
        if os.path.exists(mofile):
            with open(mofile, 'rb') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    line = line.strip('')
                    list = line.split(' ')
                    clsname = list[0]
                    metname = list[1]
                    pkg = list[2]
                    label = list[3]
                    # if pkg in self.temppkgs.keys():
                    self.mousedcases[metname] = {'label': label, 'pkg': pkg, 'clsname': clsname}

        cases = self.usedcases

        for key in cases.keys():
            if key in data.keys():
                value = data[key]
                exetime = value['exetime']
                rexetime = value['rexetime']
                errortime = value['errortime']
                loadresult = value['loadresult']
            else:
                exetime = rexetime = errortime = loadresult = [0]
            if exetime:
                tempexetime = copy.copy(exetime)
                tempexetime.remove(max(tempexetime))
                temp = cases[key]['label']
                temp_list = temp.split(':')
                writer.writerow(
                    [key, temp_list[0], temp_list[1] if len(temp_list) > 1 else temp_list[0], '点击-页面出现'] + exetime + [
                        sum(tempexetime) / (len(tempexetime) if tempexetime else 1)])
            if rexetime:
                tempretime = copy.copy(rexetime)
                tempretime.remove(max(tempretime))
                writer.writerow(
                    ['', '', '', '点击-页面内容加载完'] + rexetime + [sum(tempretime) / (len(tempretime) if tempretime else 1)])
            if errortime:
                writer.writerow(
                    ['', '','', '最大可能误差'] + errortime + [sum(errortime) / (len(errortime) if errortime else 1)])
            if loadresult:
                writer.writerow(['', '','', '上一次匹配度'] + loadresult)
                # 可用内存
                # memory = value['memory']
                # if memory:
                #     add = 0
                #     for item in memory:
                #         if item:
                #             add += float(item.split(' ')[0].strip())
                #     avg = add / len(memory)
                #     writer.writerow(['', ''] + memory + [avg])
        csvfile.close()


if __name__ == "__main__":
    print sys.argv[1]
    threads = []
    all_connect_devices = adbkit.devices()
    for device in all_connect_devices:
        if device['serialno'] in sys.argv:
            adb = adbkit.Adb(device)
            # path = '/data/local/tmp/module/busybox'
            # line = adb.shell_readline('ls -F %s' % path)
            # print '(((((((((((((((((((((((((((((('
            # print  re.search('(^(-|l-)|({0}|{0}@|{0}\*)$)'.format(os.path.split(path)[-1]), line)
            LauncherModule(adb, sys.argv[2]).parsers()
