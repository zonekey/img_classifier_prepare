#!/usr/bin/python
# coding: utf-8
#
# @file: subdir_to_labels.py
# @date: 2016-06-01
# @brief:
# @detail:
#
#################################################################

import os, sys

''' 根据当前目录下的子目录，生成 labels.txt 文件 '''

ignored = [ 'skipped', 'confused' ]


working_dir = "./"
if len(sys.argv) == 2:
    working_dir = sys.argv[1]

label = open('labels.txt', 'w')

cnt = 0
for fn in os.listdir(working_dir):
    if os.path.isdir(working_dir + '/' + fn) and fn not in ignored:
        label.write(fn + '\n')
        cnt += 1

label.close()
print cnt, "subdirs added!"




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

