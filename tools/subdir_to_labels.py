#!/usr/bin/python
# coding: utf-8
#
# @file: subdir_to_labels.py
# @date: 2016-06-01
# @brief:
# @detail:
#
#################################################################

import os

''' 根据当前目录下的子目录，生成 labels.txt 文件 '''

ignored = [ 'skipped', 'confused' ]


label = open('labels.txt', 'w')

for fn in os.listdir('./'):
    if os.path.isdir(fn) and fn not in ignored:
        label.write(fn + '\n')

label.close()





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

