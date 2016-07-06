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

data = np.arange(10000)
data = data.reshape((100, 100))

rows, cols = 100, 100 # 行列数
hcell, wcell = 0.3, 1.0 # 每个cell的高与宽

fig = plt.figure(figsize=(cols * wcell, rows * hcell))
ax = fig.add_subplot(111)
ax.axis('off')

table = ax.table(cellText=data, loc='center')
plt.savefig('table.png')



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

