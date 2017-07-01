# -*- coding: utf-8 -*-
import glob
import os
import sys

from runner import Executor

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import csv
import codecs
from tools import get_packages, echo_to_file

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_OUT = os.path.join(os.path.expanduser('~'), 'work-results')
DATA_LOCAL_TMP = '/data/local/tmp'
DATA_WORK_PATH = '/data/local/tmp/launch'


class LauncherApp(Executor):
    def __init__(self, child):
        super(LauncherApp, self).__init__(child)

    def title(self):
        return u'XXXXXX功能(待扩展功能)......'

    def desc(self):
        return u'XXXXXXXX功能说明描述信息。'

    def setup(self):
        page = super(LauncherApp, self).setup()
        return page

    def import_script(self):
        super(LauncherApp, self).import_script()
        self.generate_launch_file()

    def parsers(self):
        print 'launch work_out : ', self.work_out
        data = []
        dirs = glob.glob(os.path.join(self.work_out, self.id(), 'out', '*'))
        for dir in dirs:
            if os.path.exists(os.path.join(dir, 'cool.xml')):
                pkg_name = os.path.basename(dir)
                # xml_data = xml_parser('cool', os.path.join(dir, 'cool.xml'))
                # data += xml_data
                print 'cool'
            if os.path.exists(os.path.join(dir, 'warm.xml')):
                # pkg_name = os.path.basename(dir)
                # # xml_data = xml_parser('warm', os.path.join(dir, 'warm.xml'))
                # data += xml_data
                print 'warm'
        self.csv_generate(data, 'launch')

    def xml_parser(self, launch_type, xmlfile):
        data = []
        try:
            tree = ET.parse(xmlfile)
            root = tree.getroot()
        except Exception as e:
            print(u'读取xml文件异常')
        else:
            package = root.get('name')
            pacsize = root.get('size')
            launchtimes = root.findall('time')
            for launchtime in launchtimes:
                activname = launchtime.get('name')
                timevalues = launchtime.text
                values = timevalues.split(',') if timevalues else []
                launchdict = {'type': launch_type, 'package': package, 'activname': activname,
                              'total': pacsize,
                              'details': values}
                data.append(launchdict)
        return data

    def csv_generate(self, data, filename):
        csvfile = file(filename + '.csv', 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['应用包名', '类名', '应用大小(KB)', '启动类型', '启动时间(默认启动五次，单位：ms)', '平均值(去掉一个最大值、一个最小值再取平均)'])
        for item in data:
            package = item['package']
            type = item['type']
            activname = item['activname']
            total = item['total']
            details = item['details']
            detail_list = [int(i) for i in details]
            if detail_list:
                detail_min = min(detail_list)
                detail_max = max(detail_list)
                detail_list.remove(detail_min)
                detail_list.remove(detail_max)
            avg = sum(detail_list) / (len(detail_list) if len(detail_list) > 0 else 1)
            writer.writerow([package, activname, total, '冷启动' if type == 'cool' else '热启动', ' '.join(details), avg])
        csvfile.close()

    def generate_launch_file(self):
        count = 5
        selected_packages = []
        packages = get_packages(self.adb)
        print u'生成测试文件'
        if len(sys.argv) > 1:
            pkg_path = sys.argv[1]
            if os.path.exists(pkg_path):
                with open(pkg_path, 'r') as f:
                    for line in f:
                        pkg = line[8:].strip()
                        activity_name = ''
                        activity_label = ''
                        if pkg in packages:
                            try:
                                for activity in packages[pkg]['activities']:
                                    if activity.get('category') == 'android.intent.category.LAUNCHER':
                                        if activity_name:
                                            activity_name += ',' + activity['name']
                                        else:
                                            activity_name = activity['name']
                                            activity_label = activity['label']
                            except Exception as e:
                                print e
                            if activity_name:
                                selected_packages.append(
                                    '%s %s %s %s %s' % (pkg, activity_name, pkg, count, activity_label))
                    f.close()
                    if len(selected_packages) > 0:
                        echo_to_file(self.adb, selected_packages, DATA_WORK_PATH + '/cool.txt')
                        echo_to_file(self.adb, selected_packages, DATA_WORK_PATH + '/warm.txt')
                print 'selected_packages:', selected_packages
