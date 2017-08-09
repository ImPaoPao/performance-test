# -*- coding: utf-8 -*-
import xlwt



if __name__ == "__main__":
    # 新建一个excel文件
    file = xlwt.Workbook()
    # 新建一个sheet
    table = file.add_sheet('sheet name', cell_overwrite_ok=True)
    for i in range(0, 256):
        stylei = xlwt.XFStyle()  # 初始化样式
        patterni = xlwt.Pattern()  # 为样式创建图案
        patterni.pattern = 1  # 设置底纹的图案索引，1为实心，2为50%灰色，对                                            应为excel文件单元格格式中填充中的图案样式
        patterni.pattern_fore_colour = i  # 设置底纹的前景色，对应为excel文件单元格格式                                            中填充中的背景色
        patterni.pattern_back_colour = 35  # 设置底纹的背景色，对应为excel文件单元格格式                                            中填充中的图案颜色
        stylei.pattern = patterni  # 为样式设置图案
        table.write(i, 0, i, stylei)  # 使用样式
    file.save('colour.xls')