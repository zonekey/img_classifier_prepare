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

data = np.arange(64)
data = data.reshape((8, 8))

rows, cols = data.shape[0], data.shape[1] # 行列数
hcell, wcell = 0.3, 1.0 # 每个cell的高与宽

fig = plt.figure(figsize=(cols * wcell, rows * hcell))
ax = fig.add_subplot(111)
#ax.axis('off')

table = ax.table(cellText=data, loc='center')

# 逆时针旋转60度，现实文字标签
for i in range(0, cols):
    x, y = i * (1.0 / rows), 0.8

    bbox = { 'fc': '0.75', 'pad': 0 }
    props = { 'ha': 'left', 'va': 'bottom', 'bbox': bbox }
    plt.text(x, y, "abcdefg", props, rotation=60)

plt.savefig('table.png')



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

