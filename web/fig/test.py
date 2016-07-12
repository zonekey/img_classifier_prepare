#!/usr/bin/python
# coding: utf-8
#
# @file: test.py
# @date: 2016-07-06
# @brief:
# @detail:
#
#################################################################

''' 尝试利用 pymatplat 画 100x100 的table
'''

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import sys

width = 8
height = 8

data = np.arange(width * height)
data = data.reshape((height, width))

if sys.platform.startswith('win'):
    font_name = 'SimHei'
else:
    font_name = 'WenQuanYi Zen Hei'

font = FontProperties(font_name)
font.set_size(9) 

rows, cols = data.shape[0], data.shape[1] # 行列数
hcell, wcell = 0.3, 1.0 # 每个cell的高与宽

fig = plt.figure(figsize=(cols * wcell, rows * hcell))
ax = fig.add_subplot(111)
pos = ax.get_position()
new_pos = [pos.bounds[0], pos.bounds[1], pos.bounds[2] * 0.9, pos.bounds[3]]
ax.set_position(new_pos)
ax.axis('off')


# 单元颜色，支持高亮 
cellColors = np.full((rows, cols), 'white', dtype=object)
cellColors[4,:] = 'yellow'
cellColors[:,4] = 'yellow'

table = ax.table(cellText=data, loc='lower center', cellColours=cellColors)

#table.scale(0.9, 1.0) # table 横向缩小
#ax.set_ylim([-1.0, 0])
#ax.set_xlim([0, 1.0 / 0.9]) # table缩小，横轴也应该，这样 text 的位置可以正好


# 逆时针旋转30度，现实文字标签
for i in range(0, cols):
    x, y = (i + 0.75) * (1.0 / rows), 0.715

    bbox = { 'fc': '1.0', 'pad': 0}
    props = { 'ha': 'left', 'va': 'bottom' } # , 'bbox': bbox}

    if i == 4:
        bbox['fc'] = '0.75' # 方便突出显示
        
    plt.text(x, y, u"abc汉字+" + str(i), props, rotation=30, fontproperties=font)

    x2 = 1.0
    y2 = (0.7 / rows) * (rows - i) - 0.05
    plt.text(x2, y2, u'abc-汉字+' + str(i), props, fontproperties=font, rotation=10)

#plt.tight_layout()
plt.savefig('table.png')



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
