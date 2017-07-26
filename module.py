# -*- coding: utf-8 -*-
import codecs
import copy
import csv
import datetime
import os
from collections import OrderedDict

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from common import workdir
from runner import Executor
from tools import echo_to_file

center_module = ['launchEnglishTalk', 'launchSynStudy', 'launchSynMath', 'launchSyncEnglish', 'launchSynChinese',
                 'launchBbkMiddleMarket', 'launchOneSearch', 'launchQuestionDatabase', 'launchVision',
                 'launchVtraining', 'launchOneVideoStudy']
# 三个同步 学科同步 一键搜/智能答疑 好题 名师 视力保护 应用商店 英语听说

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


class LauncherModule(Executor):
    # def __init__(self, adb, work_out):
    #     super(LauncherModule, self).__init__(adb, work_out)

    def __init__(self, child):
        super(LauncherModule, self).__init__(child)
        print 'launcher module init ---------------'
        self.module_start = True  # 模块启动
        self.usedpkgs = dict([x for x in self.packages.items() if x[1].get('activities')])
        self.temppkgs = copy.copy(self.usedpkgs)
        self.count = 5
        self.mtype = True  # 冷热启动 默认冷
        self.init_setup()

    def init_setup(self):
        self.selm1Checked = True
        self.selm2Checked = True
        self.selm3Checked = True
        self.selm4Checked = True
        self.selm5Checked = True
        self.selm6Checked = True
        self.selm7Checked = True
        self.selm8Checked = True
        self.selm9Checked = True

        self.selsynChecked = True
        self.selpendantChecked = True
        self.selotherChecked = True

        mfile = os.path.join(workdir, 'testcase.ini')
        mofile = os.path.join(workdir, 'modulecase.txt')
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
                    if pkg in self.temppkgs.keys():
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
                    if pkg in self.temppkgs.keys():
                        self.mousedcases[metname] = {'label': label, 'pkg': pkg, 'clsname': clsname}
                        if pkg in self.mocases.keys():
                            self.mocases[pkg].append(metname)
                        else:
                            self.mocases[pkg] = [metname]
        # for key, value in self.mocases.items():
        #     print '******************', key, len(value)
        self.tempcases = copy.copy(self.usedcases)
        self.motempcases = copy.copy(self.mousedcases)
        # print 'init==============='
        # print 'usedcases:', len(self.usedcases.keys())
        # print 'tempusecases :', len(self.tempcases.keys())
        # print 'mousedcases:', len(self.mousedcases.keys())
        # print 'motemp:', len(self.motempcases.keys())

    def title(self):
        return u'启动速度'

    def desc(self):
        return u'BBK自研应用启动速度(包含图标和挂件)，和核心模块(三个同步，好题精练，名师辅导，一键搜，视力保护，应用商店，英语听说)内部主要页面切换速度'

    def track(self, data):
        if self.module_start:
            self.log(u'开始执行 ' + unicode(self.usedcases[data]['label']) + ',执行 ' + str(self.count) + ' 次')
        else:
            self.log(u'开始执行 ' + unicode(self.mousedcases[data]['label']) + ',执行 ' + str(self.count) + ' 次')

    def parsers(self):
        # print u'datas::', self.work_out
        dir_dict = {}
        # if self.module_start:
        #     dir_dict = self.usedcases
        # else:
        #     dir_dict = self.mousedcases

        work_dir = os.path.join(self.workout, self.id())
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
        self.csv_generate(data, self.id())
        self.log(self.title() + u'报告路径:' + self.workout)

    def import_script(self):
        super(LauncherModule, self).import_script()
        package_list = []
        if self.module_start:
            cases = self.usedcases
            # print u'模块启动选中:', len(self.usedcases.keys())
        else:
            cases = self.mousedcases
            # print u'页面切换选中:', len(self.mousedcases.keys())
        for key, value in cases.items():
            package_list.append(" ".join(str(i) for i in
                                         ['com.eebbk.test.performance', value['clsname'], key, key, self.count,
                                          value['pkg'], 0 if self.mtype else 1, 0, 0]))
        if len(package_list) > 0:
            echo_to_file(self.adb, package_list, self.data_work_path + '/choice.txt')

    def parser_files(self, file_dict):
        data = {}
        for key, value in file_dict.items():
            result = value
            data[key] = {'exetime': [], 'rexetime': [], 'runtime': [], 'refreshresult': [], 'memory': [],
                         'loadresult': [], 'errortime': []}
            if not os.path.exists(result):
                data[key] = {'exetime': [0], 'rexetime': [0], 'runtime': [0], 'refreshresult': [0], 'memory': [0],
                             'loadresult': [0], 'errortime': [0]}
                continue
            try:
                tree = ET.parse(result)
                root = tree.getroot()
            except Exception as e:
                # print(u'读取xml文件异常')
                data[key] = {'exetime': [0], 'rexetime': [0], 'runtime': [0], 'refreshresult': [0], 'memory': [0],
                             'loadresult': [0], 'errortime': [0]}
                continue
            else:
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
                        # print self.adb.device['device'],'============='
                        # if self.adb.device['device'] == 'S1S':
                        #     print 's1ss1s1s1s1s1=========='
                        #     exe_time = temptime
                        #     rexe_time = get_exetime(starttime, refreshtime)
                        #     data[key]['errortime'].append(error_time)
                        # else:
                        if int(loadresult) <= 10:
                            if key == 'launchVision':
                                exe_time = temptime + error_time / 2
                                rexe_time = get_exetime(starttime, refreshtime) - error_time / 2
                                data[key]['errortime'].append(error_time / 2)
                            else:
                                exe_time = temptime + error_time / 4
                                rexe_time = get_exetime(starttime, refreshtime) - error_time * 3 / 4
                                data[key]['errortime'].append(error_time)
                        else:
                            exe_time = temptime + error_time / 2
                            rexe_time = get_exetime(starttime, refreshtime) - error_time / 2
                            data[key]['errortime'].append(error_time / 2)
                        run_time = get_exetime(starttime, endtime)
                        data[key]['exetime'].append(exe_time)
                        data[key]['rexetime'].append(rexe_time)
                        data[key]['loadresult'].append(loadresult)
                        data[key]['refreshresult'].append(refreshresult)
                        data[key]['runtime'].append(run_time)
        return data

    def csv_generate(self, data, filename):
        csvfile = file(os.path.join(self.workout, filename + '.csv'), 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        if self.module_start:
            cases = self.usedcases
            writer.writerow(
                ['ID', '用例名', '测试项目', '第一次', '第二次', '第三次', '第四次', '第五次', '第六次', '第七次', '第八次', '第九次', '第十次', '平均值'])
        else:
            cases = self.mousedcases
            writer.writerow(
                ['ID', '模块', '应用名称', '测试项目', '第一次', '第二次', '第三次', '第四次', '第五次', '第六次', '第七次', '第八次', '第九次', '第十次',
                 '平均值'])
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
                case_list = cases[key]['label'].split(':')
                if self.module_start:
                    writer.writerow([key, case_list[0], '点击-页面出现'] + exetime + [
                        sum(exetime) / (len(exetime) if exetime else 1)])
                else:
                    writer.writerow([key, case_list[0], case_list[1] if len(case_list) > 1 else case_list[0],
                                     '点击-页面出现'] + exetime + [sum(exetime) / (len(exetime) if exetime else 1)])
            if rexetime:
                if self.module_start:
                    writer.writerow(
                        ['', '', '点击-页面内容加载完'] + rexetime + [sum(rexetime) / (len(rexetime) if rexetime else 1)])
                else:
                    writer.writerow(
                        ['', '', '', '点击-页面内容加载完'] + rexetime + [sum(rexetime) / (len(rexetime) if rexetime else 1)])
            if errortime:
                if self.module_start:
                    writer.writerow(
                        ['', '', '最大可能误差'] + errortime + [sum(errortime) / (len(errortime) if errortime else 1)])
                else:
                    writer.writerow(
                        ['', '', '', '最大可能误差'] + errortime + [sum(errortime) / (len(errortime) if errortime else 1)])
            if loadresult:
                if self.module_start:
                    writer.writerow(['', '', '上一次匹配度'] + loadresult)
                else:
                    writer.writerow(['', '', '', '上一次匹配度'] + loadresult)
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

    def setup(self):
        # print  '----module insetup ------'
        # print 'usedcases:', len(self.usedcases.keys())
        # print 'tempusecases :', len(self.tempcases.keys())
        # print 'mousedcases:', len(self.mousedcases.keys())
        # print 'motemp:', len(self.motempcases.keys())
        page = super(LauncherModule, self).setup()
        page.setButtonText(QWizard.FinishButton, u'保存')
        page.setButtonText(QWizard.CancelButton, u'取消')
        check = QCheckBox(u'继续上一次的测试,如果执行失败，帮助导出测试结果？')
        check.setEnabled(False)

        self.radio1 = QRadioButton(u'模块启动速度')
        self.radio1.setChecked(self.module_start)
        self.radio1.toggled[bool].connect(self.radio1Toggled)
        self.radio2 = QRadioButton(u'核心模块页面切换速度')
        self.radio2.setChecked(not self.module_start)
        self.radio2.toggled[bool].connect(self.radio2Toggled)

        self.checbox3 = QCheckBox(u'冷启动')
        self.checbox4 = QCheckBox(u'热启动')
        # self.checbox3.setCheckState(Qt.Checked)
        self.checbox3.setCheckState(Qt.Checked if self.mtype else Qt.Unchecked)
        self.checbox4.setCheckState(Qt.Unchecked if self.mtype else Qt.Checked)

        self.checbox3.stateChanged[int].connect(self.checbox3Toggled)
        self.checbox3.setEnabled(self.module_start)
        self.checbox4.setEnabled(self.module_start)
        self.checbox4.stateChanged[int].connect(self.checbox4Toggled)
        self.edit1 = QLineEdit(str(self.count))
        self.edit1.setValidator(QIntValidator())
        self.edit1.textChanged[str].connect(self.edit1Changed)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(u'测试次数'), 0, 0)
        gridLayout.addWidget(self.edit1, 0, 1)
        gridLayout.addWidget(self.checbox3, 1, 0)
        gridLayout.addWidget(self.checbox4, 2, 0)
        itemLayout = QVBoxLayout()
        itemLayout.addWidget(self.radio1)

        buttonlayout = QGridLayout()
        self.buttonwidget = QWidget()

        # buttonlayout.addWidget(QLabel(u'常用组合:'), 0, 0)
        # self.selall = QCheckBox(u'全选')
        self.selsyn = QCheckBox(u'核心模块(图标)')
        self.selpendant = QCheckBox(u'挂件')
        self.selother = QCheckBox(u'其它(不包含挂件和核心模块)')

        # buttonlayout.addWidget(self.selall, 1, 1)
        buttonlayout.addWidget(self.selsyn, 2, 1)
        buttonlayout.addWidget(self.selpendant, 3, 1)
        buttonlayout.addWidget(self.selother, 4, 1)
        self.buttonwidget.setLayout(buttonlayout)
        itemLayout.addWidget(self.buttonwidget)

        itemLayout.addWidget(self.radio2)
        buttonlayout2 = QGridLayout()
        self.buttonwidget2 = QWidget()
        self.selm1 = QCheckBox(u'同步语文')
        self.selm2 = QCheckBox(u'同步数学')
        self.selm3 = QCheckBox(u'同步英语')
        self.selm4 = QCheckBox(u'应用商店')
        self.selm5 = QCheckBox(u'好题精炼')
        self.selm6 = QCheckBox(u'名师辅导')
        self.selm7 = QCheckBox(u'视力保护')
        self.selm8 = QCheckBox(u'学科同步')
        self.selm9 = QCheckBox(u'英语听说')

        # 临时选择

        ###


        buttonlayout2.addWidget(self.selm1, 2, 1)
        buttonlayout2.addWidget(self.selm2, 3, 1)
        buttonlayout2.addWidget(self.selm3, 1, 1)
        buttonlayout2.addWidget(self.selm4, 4, 1)
        buttonlayout2.addWidget(self.selm5, 5, 1)
        buttonlayout2.addWidget(self.selm6, 6, 1)
        buttonlayout2.addWidget(self.selm7, 7, 1)
        buttonlayout2.addWidget(self.selm8, 8, 1)
        buttonlayout2.addWidget(self.selm9, 9, 1)

        self.buttonwidget2.setLayout(buttonlayout2)
        itemLayout.addWidget(self.buttonwidget2)
        self.buttonwidget.setEnabled(self.module_start)
        self.buttonwidget2.setDisabled(self.module_start)

        itemLayout.addStretch()
        itemLayout.addLayout(gridLayout)

        self.itemGroup = QGroupBox(u'启动速度测试参数')
        self.itemGroup.setLayout(itemLayout)

        self.list = QListWidget(page.wizard())
        self.list2 = QListWidget(page.wizard())
        self.selallmodule = QListWidgetItem(u'全选')
        self.list2.addItem(self.selallmodule)
        self.selallin = QListWidgetItem(u'全选')
        self.list.addItem(self.selallin)
        for key in self.tempcases.keys():
            label = self.tempcases[key]['label'].replace("\n", "")
            item = QListWidgetItem(unicode(label))
            if key in self.usedcases.keys():
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            item.setData(1, QVariant(key))
            self.list.addItem(item)

        for key in self.motempcases.keys():
            label = self.motempcases[key]['label'].replace("\n", "")
            item = QListWidgetItem(unicode(label))
            if key in self.mousedcases.keys():
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            item.setData(1, QVariant(key))
            self.list2.addItem(item)

        #
        self.selallin.setCheckState(Qt.Checked if self.list.count() - 1 == len(self.usedcases.keys()) else Qt.Unchecked)
        self.selallin.setData(1, QVariant('selall'))
        #
        self.selallmodule.setCheckState(
            Qt.Checked if self.list2.count() - 1 == len(self.mousedcases.keys()) else Qt.Unchecked)
        self.selallmodule.setData(1, QVariant('selallmodule'))

        self.list.itemChanged.connect(self.itemChanged)
        self.list2.itemChanged.connect(self.itemChanged2)
        self.list.setEnabled(self.module_start)
        self.list2.setDisabled(self.module_start)

        self.selsyn.setChecked(self.selsynChecked)
        self.selpendant.setChecked(self.selpendantChecked)
        self.selother.setChecked(self.selotherChecked)
        # self.selall.setCheckState(Qt.Checked)
        # self.selall.stateChanged[int].connect(self.selallChanged)
        self.selsyn.stateChanged[int].connect(self.selsynChanged)
        self.selother.stateChanged[int].connect(self.selotherChanged)
        self.selpendant.stateChanged[int].connect(self.selpendantChanged)

        self.selm1.setChecked(self.selm1Checked)
        self.selm2.setChecked(self.selm2Checked)
        self.selm3.setChecked(self.selm3Checked)
        self.selm4.setChecked(self.selm4Checked)
        self.selm5.setChecked(self.selm5Checked)
        self.selm6.setChecked(self.selm6Checked)
        self.selm7.setChecked(self.selm7Checked)
        self.selm8.setChecked(self.selm8Checked)
        self.selm9.setChecked(self.selm9Checked)
        self.selm1.stateChanged[int].connect(self.selm1Changed)
        self.selm2.stateChanged[int].connect(self.selm2Changed)
        self.selm3.stateChanged[int].connect(self.selm3Changed)
        self.selm4.stateChanged[int].connect(self.selm4Changed)
        self.selm5.stateChanged[int].connect(self.selm5Changed)
        self.selm6.stateChanged[int].connect(self.selm6Changed)
        self.selm7.stateChanged[int].connect(self.selm7Changed)
        self.selm8.stateChanged[int].connect(self.selm8Changed)
        self.selm9.stateChanged[int].connect(self.selm9Changed)

        listLayout = QVBoxLayout()
        listLayout.addWidget(self.list)
        listLayout.addWidget(self.list2)
        self.listGroup = QGroupBox(u'模块启动可选用例')
        self.listGroup.setLayout(listLayout)

        itemLayout = QHBoxLayout()
        itemLayout.addWidget(self.itemGroup)
        itemLayout.addWidget(self.listGroup)
        itemLayout.setStretch(0, 1)
        itemLayout.setStretch(1, 3)

        layout = QVBoxLayout()
        layout.addWidget(check)
        layout.addLayout(itemLayout)
        page.setLayout(layout)
        return page

    def itemChanged2(self, item):
        metname = str(item.data(1).toPyObject())
        if metname == 'selallmodule':
            # if item.checkState() ==Qt.Unchecked:
            #     print 'if ',len(self.mousedcases.keys())
            #     # if len(self.mousedcases.keys())!=0 and self.list2.count()-1 != len(self.mousedcases.keys()):
            #     if self.list2.count() - 1 == len(self.mousedcases.keys()):
            #         pass
            #     else:
            #         print u'非点击全选触发'
            for i in range(self.list2.count()):
                self.list2.item(i).setCheckState(item.checkState())
            self.selm1.setChecked(item.checkState())
            self.selm2.setChecked(item.checkState())
            self.selm3.setChecked(item.checkState())
            self.selm4.setChecked(item.checkState())
            self.selm5.setChecked(item.checkState())
            self.selm6.setChecked(item.checkState())
            self.selm7.setChecked(item.checkState())
            self.selm8.setChecked(item.checkState())
            self.selm9.setChecked(item.checkState())
            # print len(self.mousedcases.keys())
        else:
            pkg = self.motempcases[metname]['pkg']
            if item.checkState() == Qt.Checked:
                self.mousedcases[metname] = self.motempcases.get(metname)
                count = 0
                for m, value in self.mousedcases.items():
                    if value['pkg'] == pkg:
                        count += 1
                if len(self.mocases[pkg]) == count:
                    if pkg == 'com.eebbk.synchinese':
                        self.selm1.setCheckState(Qt.Checked)
                    if pkg == 'com.eebbk.synmath':
                        self.selm2.setCheckState(Qt.Checked)
                    if pkg == 'com.eebbk.syncenglish':
                        self.selm3.setCheckState(Qt.Checked)
                    if pkg == 'com.eebbk.bbkmiddlemarket':
                        self.selm4.setCheckState(Qt.Checked)
                    if pkg == 'com.eebbk.questiondatabase':
                        self.selm5.setCheckState(Qt.Checked)
                    if pkg == 'com.eebbk.vtraining':
                        self.selm6.setCheckState(Qt.Checked)
                    if pkg == 'com.eebbk.vision':
                        self.selm7.setCheckState(Qt.Checked)
                    if pkg == 'com.eebbk.synstudy':
                        self.selm8.setCheckState(Qt.Checked)
                    if pkg == 'com.eebbk.englishtalk':
                        self.selm9.setCheckState(Qt.Checked)
            else:
                self.mousedcases.pop(metname, 'None')
                if pkg == 'com.eebbk.synchinese':
                    if self.selm1.isChecked():
                        self.selm1.setCheckState(Qt.Unchecked)
                if pkg == 'com.eebbk.synmath':
                    if self.selm2.isChecked():
                        self.selm2.setCheckState(Qt.Unchecked)
                if pkg == 'com.eebbk.syncenglish':
                    if self.selm3.isChecked():
                        self.selm3.setCheckState(Qt.Unchecked)
                if pkg == 'com.eebbk.bbkmiddlemarket':
                    if self.selm4.isChecked():
                        self.selm4.setCheckState(Qt.Unchecked)
                if pkg == 'com.eebbk.questiondatabase':
                    if self.selm5.isChecked():
                        self.selm5.setCheckState(Qt.Unchecked)
                if pkg == 'com.eebbk.vtraining':
                    if self.selm6.isChecked():
                        self.selm6.setCheckState(Qt.Unchecked)
                if pkg == 'com.eebbk.vision':
                    if self.selm7.isChecked():
                        self.selm7.setCheckState(Qt.Unchecked)
                if pkg == 'com.eebbk.synstudy':
                    if self.selm8.isChecked():
                        self.selm8.setCheckState(Qt.Unchecked)
                if pkg == 'com.eebbk.englishtalk':
                    if self.selm9.isChecked():
                        self.selm9.setCheckState(Qt.Unchecked)
            #
            # print 'end:', len(self.mousedcases.keys())

            if len(self.mousedcases.keys()) == self.list2.count() - 1:
                self.list2.item(0).setCheckState(Qt.Checked)
            if len(self.mousedcases.keys()) == 0:
                self.list2.item(0).setCheckState(Qt.Unchecked)

    def itemChanged(self, item):
        metname = str(item.data(1).toPyObject())
        if metname == 'selall':
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(item.checkState())
            self.selsyn.setChecked(item.checkState())
            self.selother.setChecked(item.checkState())
            self.selpendant.setChecked(item.checkState())
        else:
            if item.checkState() == Qt.Checked:
                self.usedcases[metname] = self.tempcases.get(metname)
                count1 = count2 = count3 = 0
                temp1 = temp2 = temp3 = 0
                for m in self.tempcases.keys():
                    if m in center_module:
                        if m in self.usedcases.keys():
                            count1 += 1
                        temp1 += 1
                    if 'Pendant' not in m and m not in center_module and m != 'selall':
                        if m in self.usedcases.keys():
                            count3 += 1
                        temp3 += 1
                    if 'Pendant' in m:
                        if m in self.usedcases.keys():
                            count2 += 1
                        temp2 += 1
                # print count1, count2, count3
                # print '*********************'
                if temp1 == count1:
                    self.selsyn.setCheckState(Qt.Checked)
                if temp2 == count2:
                    self.selpendant.setCheckState(Qt.Checked)
                if temp3 == count3:
                    self.selother.setCheckState(Qt.Checked)
            else:
                self.usedcases.pop(metname, 'None')
                if metname in center_module:
                    if self.selsyn.isChecked():
                        self.selsyn.setCheckState(Qt.Unchecked)
                if 'Pendant' not in metname and metname not in center_module and metname != 'selall':
                    if self.selother.isChecked():
                        self.selother.setCheckState(Qt.Unchecked)
                if 'Pendant' in metname:
                    if self.selpendant.isChecked():
                        self.selpendant.setCheckState(Qt.Unchecked)

        # print len(self.usedcases.keys()) == self.list.count() - 1
        if len(self.usedcases.keys()) == self.list.count() - 1:
            self.list.item(0).setCheckState(Qt.Checked)
        if len(self.usedcases.keys()) == 0:
            self.list.item(0).setCheckState(Qt.Unchecked)

    def radio1Toggled(self, checked):
        # print 'radio1:',checked,self.module_start
        if checked:
            # print 'radio1 checked ',checked
            self.module_start = True
            self.buttonwidget.setEnabled(checked)
            self.buttonwidget2.setDisabled(checked)
            # self.listGroup.setEnabled(checked)
            self.list.setEnabled(checked)
            self.list2.setDisabled(checked)
            self.checbox3.setEnabled(True)
            self.checbox4.setEnabled(True)

    def radio2Toggled(self, checked):
        # print 'radio2:', checked, self.module_start
        if checked:
            # print 'radio2 checked ',checked
            self.module_start = False
            self.buttonwidget.setDisabled(checked)
            self.buttonwidget2.setEnabled(checked)
            # self.listGroup.setDisabled(checked)
            self.list.setDisabled(checked)
            self.list2.setEnabled(checked)
            self.checbox3.setDisabled(True)
            self.checbox4.setDisabled(True)

    def checbox3Toggled(self, state):
        # print 'checbox3', state
        if state:
            self.mtype = True
        self.checbox4.setChecked(not state)

    def checbox4Toggled(self, state):
        # print 'checbox4', state
        if state:
            self.mtype = False
        self.checbox3.setChecked(not state)

    def edit1Changed(self, text):
        if str(text).isdigit():
            self.count = int(text)
        else:
            self.edit1.undo()

    def selallChanged(self, state):
        # print u'全选:', state
        for i in range(self.list.count()):
            self.list.item(i).setCheckState(state)

    def selsynChanged(self, state):
        # print u'核心模块:', state
        if state:
            self.selsynChecked = True
        else:
            self.selsynChecked = False
        self.checkboxToggled1(self.selsyn, state)

    def selotherChanged(self, state):
        # print u'其它不包含挂件和核心:', state
        if state:
            self.selotherChecked = True
        else:
            self.selotherChecked = False
        self.checkboxToggled1(self.selother, state)

    def selpendantChanged(self, state):
        # print u'挂件:', state
        if state:
            self.selpendantChecked = True
        else:
            self.selpendantChecked = False
        self.checkboxToggled1(self.selpendant, state)

    # 页面切换速度
    def selm1Changed(self, state):
        # print 'selm1Changed', state
        if state:
            self.selm1Checked = True
        else:
            self.selm1Checked = False
        self.checkboxToggled('com.eebbk.synchinese', state)

    def selm2Changed(self, state):
        # print 'selm2Changed'
        if state:
            self.selm2Checked = True
        else:
            self.selm2Checked = False
        self.checkboxToggled('com.eebbk.synmath', state)

    def selm3Changed(self, state):
        # print 'selm3Changed'
        if state:
            self.selm3Checked = True
        else:
            self.selm3Checked = False
        self.checkboxToggled('com.eebbk.syncenglish', state)

    def selm4Changed(self, state):
        # print 'selm4Changed'
        if state:
            self.selm4Checked = True
        else:
            self.selm4Checked = False
        self.checkboxToggled('com.eebbk.bbkmiddlemarket', state)

    def selm5Changed(self, state):
        # print 'selm5Changed'
        if state:
            self.selm5Checked = True
        else:
            self.selm5Checked = False
        self.checkboxToggled('com.eebbk.questiondatabase', state)

    def selm6Changed(self, state):
        # print 'selm6Changed'
        if state:
            self.selm6Checked = True
        else:
            self.selm6Checked = False
        self.checkboxToggled('com.eebbk.vtraining', state)

    def selm7Changed(self, state):
        # print 'selm7Changed'
        if state:
            self.selm7Checked = True
        else:
            self.selm7Checked = False
        self.checkboxToggled('com.eebbk.vision', state)

    def selm8Changed(self, state):
        # print 'selm8Changed'
        if state:
            self.selm8Checked = True
        else:
            self.selm8Checked = False
        self.checkboxToggled('com.eebbk.synstudy', state)

    def selm9Changed(self, state):
        # print 'selm9Changed'
        if state:
            self.selm9Checked = True
        else:
            self.selm9Checked = False
        self.checkboxToggled('com.eebbk.englishtalk', state)

    def checkboxToggled(self, pkg, state):
        if not state:
            count = 0
            for key, value in self.mousedcases.items():
                if value['pkg'] == pkg:
                    count += 1
            if len(self.mocases[pkg]) == count:
                pass
            else:
                return
        for i in range(self.list2.count()):
            metname = str(self.list2.item(i).data(1).toPyObject())
            if metname == 'selallmodule':
                continue
            if self.motempcases[metname]['pkg'] == pkg:
                if self.list2.item(i).checkState() != state:
                    self.list2.item(i).setCheckState(state)
        # print u'选中:', len(self.mousedcases.keys())
        # print len(self.mousedcases.keys()), self.list2.count()
        if len(self.mousedcases.keys()) == self.list2.count() - 1:
            self.list2.item(0).setCheckState(Qt.Checked)
        if len(self.mousedcases.keys()) == 0:
            self.list2.item(0).setCheckState(Qt.Unchecked)

    def checkboxToggled1(self, sender, state):
        if not state:
            count1 = count2 = count3 = 0
            temp1 = temp2 = temp3 = 0
            for m in self.tempcases.keys():
                if m in center_module:
                    if m in self.usedcases.keys():
                        count1 += 1
                    temp1 += 1
                if 'Pendant' not in m and m not in center_module and m != 'selall':
                    if m in self.usedcases.keys():
                        count3 += 1
                    temp3 += 1
                if 'Pendant' in m:
                    if m in self.usedcases.keys():
                        count2 += 1
                    temp2 += 1
            # print count1, count2, count3
            # print '*********************'
            if count1 == temp1:
                pass
            elif count2 == temp2:
                pass
            elif count3 == temp3:
                pass
            else:
                return

        for i in range(self.list.count()):
            metname = str(self.list.item(i).data(1).toPyObject())
            if sender == self.selpendant:
                if 'Pendant' in metname:
                    if self.list.item(i).checkState() != state:
                        self.list.item(i).setCheckState(state)
            elif sender == self.selsyn:
                if metname in center_module:
                    if self.list.item(i).checkState() != state:
                        self.list.item(i).setCheckState(state)
            elif sender == self.selother:
                if 'Pendant' not in metname and metname not in center_module and metname != 'selall':
                    if self.list.item(i).checkState() != state:
                        self.list.item(i).setCheckState(state)
        # print u'选中:', len(self.usedcases.keys())
        # print len(self.usedcases.keys()), self.list.count()
        if len(self.usedcases.keys()) == self.list.count() - 1:
            self.list.item(0).setCheckState(Qt.Checked)
        if len(self.usedcases.keys()) == 0:
            self.list.item(0).setCheckState(Qt.Unchecked)
