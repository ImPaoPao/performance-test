# -*- coding: utf-8 -*-
import codecs
import copy
import csv
import datetime
import os

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
        self.module_start = True  # 模块启动
        self.usedpkgs = dict([x for x in self.packages.items() if x[1].get('activities')])
        self.temppkgs = copy.copy(self.usedpkgs)
        self.count = 5
        self.mtype = True  # 冷热启动 默认冷

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
        print u'datas::', self.work_out
        dir_dict = {}
        work_dir = os.path.join(self.work_out, self.id())
        for root, dirs, files in os.walk(work_dir):
            for name in files:
                if name == 'result.xml':
                    result = os.path.join(root, 'result.xml')
                    if os.path.exists(result):
                        dir_dict[os.path.basename(root)] = result
        data = self.parser_files(dir_dict)
        self.csv_generate(data, self.id())
        self.log(self.title() + u'报告路径:' + self.work_out)

    def import_script(self):
        super(LauncherModule, self).import_script()
        package_list = []
        print self.module_start
        if self.module_start:
            cases = self.usedcases
            print u'模块启动选中:', len(self.usedcases.keys())
        else:
            cases = self.mousedcases
            print u'页面切换选中:', len(self.mousedcases.keys())
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
            try:
                tree = ET.parse(result)
                root = tree.getroot()
            except Exception as e:
                print(u'读取xml文件异常')
            else:
                segments = root.findall('Segment')
                data[key] = {'exetime': [], 'rexetime': [], 'runtime': [], 'refreshresult': [], 'memory': [],
                             'loadresult': [], 'errortime': [], 'lastloadresult': []}
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
                        error_time = get_exetime(lasttime, loadtime)
                        temptime = get_exetime(starttime, lasttime)
                        if int(loadresult) <= 10:
                            exe_time = temptime  # + error_time / 4
                            rexe_time = get_exetime(starttime, refreshtime) - error_time  # * 3 / 4
                        else:
                            exe_time = temptime + error_time * 1 / 4
                            rexe_time = get_exetime(starttime, refreshtime) - error_time * 3 / 4
                        run_time = get_exetime(starttime, endtime)
                        data[key]['exetime'].append(exe_time)
                        data[key]['rexetime'].append(rexe_time)
                        data[key]['loadresult'].append(loadresult)
                        data[key]['refreshresult'].append(refreshresult)
                        data[key]['runtime'].append(run_time)
                        data[key]['errortime'].append(error_time / 2)
        return data

    def csv_generate(self, data, filename):
        csvfile = file(os.path.join(self.work_out, filename + '.csv'), 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(
            ['ID', '用例名', '测试项目', '第一次', '第二次', '第三次', '第四次', '第五次', '第六次', '第七次', '第八次', '第九次', '第十次', '平均值'])
        for key, value in data.items():
            exetime = value['exetime']
            rexetime = value['rexetime']
            errortime = value['errortime']
            loadresult = value['loadresult']
            # refreshresult = value['refreshresult']
            if exetime:
                writer.writerow([key, self.usedcases[key]['label'], '点击-页面出现'] + exetime + [
                    sum(exetime) / (len(exetime) if exetime else 1)])
            if rexetime:
                writer.writerow(
                    ['', '', '点击-页面内容加载完'] + rexetime + [sum(rexetime) / (len(rexetime) if rexetime else 1)])
            if errortime:
                writer.writerow(['', '', '最大误差'] + errortime + [sum(errortime) / (len(errortime) if errortime else 1)])
            if loadresult:
                writer.writerow(['', '', '上一次匹配度'] + loadresult + [0])
            # 可用内存
            memory = value['memory']
            if memory:
                add = 0
                for item in memory:
                    if item:
                        add += float(item.split(' ')[0].strip())
                avg = add / len(memory)
                writer.writerow(['', ''] + memory + [avg])
        csvfile.close()

    def setup(self):
        page = super(LauncherModule, self).setup()
        mfile = os.path.join(workdir, 'testcase.ini')
        mofile = os.path.join(workdir, 'modulecase.txt')
        self.usedcases = {}
        self.mousedcases = {}
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
        self.tempcases = copy.copy(self.usedcases)
        self.motempcases = copy.copy(self.mousedcases)

        check = QCheckBox(u'继续上一次的测试,如果执行失败，帮助导出测试结果？')
        check.setEnabled(False)

        self.radio1 = QRadioButton(u'模块启动速度')
        self.radio1.setChecked(self.module_start)
        self.radio1.toggled[bool].connect(self.radio1Toggled)
        self.radio2 = QRadioButton(u'核心模块页面切换速度')
        self.radio2.toggled[bool].connect(self.radio2Toggled)

        self.checbox3 = QCheckBox(u'冷启动')
        self.checbox4 = QCheckBox(u'热启动')
        self.checbox3.setCheckState(Qt.Checked)
        self.checbox3.stateChanged[int].connect(self.checbox3Toggled)
        self.checbox3.setEnabled(False)
        self.checbox4.setEnabled(False)
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
        self.selall = QCheckBox(u'全选')
        self.selsyn = QCheckBox(u'9个核心模块')
        self.selpendant = QCheckBox(u'挂件')
        self.selother = QCheckBox(u'其它(不包含挂件和核心模块)')
        self.checkbox_list = [self.selall, self.selsyn, self.selpendant, self.selother]

        buttonlayout.addWidget(self.selall, 1, 1)
        buttonlayout.addWidget(self.selsyn, 2, 1)
        buttonlayout.addWidget(self.selpendant, 3, 1)
        buttonlayout.addWidget(self.selother, 4, 1)
        self.buttonwidget.setLayout(buttonlayout)

        # itemLayout.addLayout(buttonlayout)
        itemLayout.addWidget(self.buttonwidget)

        itemLayout.addWidget(self.radio2)
        itemLayout.addStretch()
        itemLayout.addLayout(gridLayout)
        self.itemGroup = QGroupBox(u'启动速度测试参数')
        self.itemGroup.setLayout(itemLayout)

        self.selall.setCheckState(Qt.Checked)
        self.selall.stateChanged[int].connect(self.selallChanged)
        self.selsyn.stateChanged[int].connect(self.selsynChanged)
        self.selother.stateChanged[int].connect(self.selotherChanged)
        self.selpendant.stateChanged[int].connect(self.selpendantChanged)
        self.list = QListWidget(page.wizard())
        self.list.itemChanged.connect(self.itemChanged)
        self.list2 = QListWidget(page.wizard())
        self.list2.itemChanged.connect(self.itemChanged2)
        self.list.setEnabled(self.module_start)
        self.list2.setDisabled(self.module_start)
        self.selallin = QListWidgetItem(u'全选')
        self.selallin.setCheckState(Qt.Checked)
        self.selallin.setData(1, QVariant('selall'))
        self.list.addItem(self.selallin)
        # for key in self.temppkgs.keys():
        #     item = QListWidgetItem(key)
        #     item.setCheckState(Qt.Checked)
        #     item.setData(1, QVariant(key))
        #     self.list.addItem(item)
        for key in self.tempcases.keys():
            label = self.tempcases[key]['label'].replace("\n", "")
            item = QListWidgetItem(unicode(label))
            item.setCheckState(Qt.Checked)
            item.setData(1, QVariant(key))
            self.list.addItem(item)
        for key in self.motempcases.keys():
            label = self.motempcases[key]['label'].replace("\n", "")
            item = QListWidgetItem(unicode(label))
            item.setCheckState(Qt.Checked)
            item.setData(1, QVariant(key))
            self.list2.addItem(item)

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
        print 'itemchanged 2 '

    def itemChanged(self, item):
        pkg = str(item.data(1).toPyObject())
        if pkg == 'selall':
            for i in range(self.list.count()):
                self.list.item(i).setCheckState(item.checkState())
        else:
            if item.checkState() == Qt.Checked:
                self.usedcases[pkg] = self.tempcases.get(pkg)
            else:
                self.usedcases.pop(pkg, 'None')

    def radio1Toggled(self, checked):
        self.module_start = checked
        if checked:
            self.buttonwidget.setEnabled(checked)
            # self.listGroup.setEnabled(checked)
            self.list.setEnabled(checked)
            self.list2.setDisabled(checked)

    def radio2Toggled(self, checked):
        if checked:
            self.buttonwidget.setDisabled(checked)
            # self.listGroup.setDisabled(checked)
            self.list.setDisabled(checked)
            self.list2.setEnabled(checked)

    def checbox3Toggled(self, state):
        print 'checbox3', state
        if state:
            self.mtype = True
        self.checbox4.setChecked(not state)

    def checbox4Toggled(self, state):
        print 'checbox4', state
        if state:
            self.mtype = False
        self.checbox3.setChecked(not state)

    def edit1Changed(self, text):
        if str(text).isdigit():
            self.count = int(text)
        else:
            self.edit1.undo()

    def selallChanged(self, state):
        print u'全选:', state
        if state:
            self.selpendant.setChecked(not state)
            self.selother.setChecked(not state)
            self.selsyn.setChecked(not state)
        else:
            i = 0
            for box in self.checkbox_list:
                if not box.isChecked():
                    i += 1
            if i == len(self.checkbox_list):
                self.selsyn.setChecked(not state)
                self.selsyn.setCheckState(not state)
        for i in range(self.list.count()):
            self.list.item(i).setCheckState(state)

    def selsynChanged(self, state):
        print u'9个核心模块:', state
        if state:
            self.selpendant.setChecked(not state)
            self.selother.setChecked(not state)
            self.selall.setChecked(not state)
        else:
            i = 0
            for box in self.checkbox_list:
                if not box.isChecked():
                    i += 1
            if i == len(self.checkbox_list):
                self.selall.setChecked(not state)
                self.selall.setCheckState(not state)
        for i in range(self.list.count()):
            metname = str(self.list.item(i).data(1).toPyObject())
            # pkg = str(self.list.item(i).data(2).toPyObject())
            if metname in center_module:
                self.list.item(i).setCheckState(state)
            else:
                self.list.item(i).setCheckState(not state)
                # pkg = str(self.list.item(i).data(1).toPyObject())
                # print pkg

    def selotherChanged(self, state):
        print u'其它不包含挂件和核心:', state
        if state:
            self.selpendant.setChecked(not state)
            self.selall.setChecked(not state)
            self.selsyn.setChecked(not state)
        else:
            i = 0
            for box in self.checkbox_list:
                if not box.isChecked():
                    i += 1
            if i == len(self.checkbox_list):
                self.selsyn.setChecked(not state)
                self.selsyn.setCheckState(not state)
        for i in range(self.list.count()):
            metname = str(self.list.item(i).data(1).toPyObject())
            if 'Pendant' not in metname and metname not in center_module:
                self.list.item(i).setCheckState(state)
            else:
                self.list.item(i).setCheckState(not state)

    def selpendantChanged(self, state):
        print u'挂件:', state
        if state:
            self.selother.setChecked(not state)
            self.selall.setChecked(not state)
            self.selsyn.setChecked(not state)
        else:
            i = 0
            for box in self.checkbox_list:
                if not box.isChecked():
                    i += 1
            if i == len(self.checkbox_list):
                self.selsyn.setChecked(not state)
                self.selsyn.setCheckState(not state)
        for i in range(self.list.count()):
            metname = str(self.list.item(i).data(1).toPyObject())
            if 'Pendant' in metname:
                self.list.item(i).setCheckState(state)
            else:
                self.list.item(i).setCheckState(not state)
