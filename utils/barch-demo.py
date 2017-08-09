# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

plt.rcdefaults()

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
# plt.rcdefaults()
# fig, ax = plt.subplots()
#
# # Example data
# people = ('pkg1', 'pkg2')
# y_pos = [1,4]
# performance = 3 + 10 * np.random.rand(len(people))
# error = np.random.rand(len(people))
#
# ax.barh(y_pos, performance, xerr=None, align='center',
#         color='green', ecolor='black')
# ax.set_yticks(y_pos)
# ax.set_yticklabels(people)
# ax.invert_yaxis()  # labels read top-to-bottom
# ax.set_xlabel(u'卡顿次数',fontproperties='SimHei')
# ax.set_title(u'进程卡顿统计',fontproperties='SimHei')
#
# plt.show()
"""
Bar chart demo with pairs of bars grouped for easy comparison.
"""
import numpy as np
import matplotlib.pyplot as plt
#
# n_groups = 5
#
# means_men = (2, 5, 3, 9, 7,2, 5, 3, 9, 7)
# means_men_ticks = ('paaaaaaaakg1', 'pxxxxxxxxxxxxxxxxxxxxkg2', 'pkgcccc3', 'com.eebbk.time1', 'pkg5','pkg1', 'pkg2', 'pkg3', 'pkg4', 'pkg5')
# std_men = (2, 3, 4, 1, 2)
#
# fig, ax = plt.subplots()
# # def barh(bottom, width, height=0.8, left=None, hold=None, **kwargs):
# #def bar(left, height, width=0.8, bottom=None, hold=None, data=None, **kwargs):
# index = np.arange(len(means_men))
# bar_width = 0.3
# opacity = 0.4
# error_config = {'ecolor': '0.3'}
#
# # rects1 = plt.bar(index, means_men, bar_width,
# #                  alpha=opacity,
# #                  color='b',
# #                  yerr=None,
# #                  align='center',
# #                  error_kw=error_config,
# #                  label='Men')
# rects2 = plt.barh(index,means_men)
# plt.ylabel(u'进程名称',fontproperties='SimHei')
# plt.xlabel(u'卡顿次数(单位:次)',fontproperties='SimHei')
# plt.title(u'性能监控统计',fontproperties='SimHei')
# for a,b in zip(index,means_men):
#     print a,b
#     plt.text(b+0.1, a, '%.0f' % b, ha='center', va= 'bottom',fontsize=7)
# plt.yticks(index, means_men_ticks)
# plt.legend()
# plt.tight_layout()
#
# plt.show()
import xlsxwriter

workbook = xlsxwriter.Workbook('chart.xlsx')
worksheet = workbook.add_worksheet()

# Create a new Chart object.
chart = workbook.add_chart({'type': 'bar'})

# Write some data to add to plot on the chart.
data = [
['q', 'w', 'e', 't', 'y'],
    [1, 2, 3, 4, 5],
    [2, 4, 6, 8, 10],
    [3, 6, 9, 12, 15],
]

worksheet.write_column('A1', data[0])  # 按列插入
worksheet.write_column('B1', data[1])
worksheet.write_column('C1', data[2])

chart = workbook.add_chart({'type': 'bar'})
# Configure the chart. In simplest case we add one or more data series.
chart.add_series({'values': '=Sheet1!$B$2:$B$5','categories':'=Sheet1!$A$2:$A$5','data_labels': {'value': True}})

# Insert the chart into the worksheet.
worksheet.insert_chart('F7', chart)

workbook.close()