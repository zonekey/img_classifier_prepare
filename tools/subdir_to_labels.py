#!/usr/bin/python
# coding: utf-8
#
# @file: subdir_to_labels.py
# @date: 2016-06-07 如果labels0.txt 已经存在，则不修改 labels0 中对应的 labels 文件的顺序...
# @brief:
# @detail:
#
#################################################################

import os, sys

''' 根据当前目录下的子目录，生成 labels.txt 文件 '''

ignored = [ 'skipped', 'confused' ]
catalogs = []

# labels0.txt 中对应着模型训练的类别 ...
try:
    with open('labels0.txt', 'r') as f:
        for line in f:
            c = line.strip()
            if len(c) > 1:
                catalogs.append(c)
except:
    pass
print 'orig catalogs:', len(catalogs)

# 工作目录中，自动添加非 labels0 中的子目录作为标签 ...
working_dir = "./"
if len(sys.argv) == 2:
    working_dir = sys.argv[1]

cnt = 0
label = open('labels.txt', 'w')
for c in catalogs:
    label.write(c + '\n')
    cnt += 1

for fn in os.listdir(working_dir):
    if os.path.isdir(working_dir + '/' + fn) and fn not in ignored and fn not in catalogs:
        label.write(fn + '\n')
        cnt += 1

label.close()
print cnt, "subdirs added!"




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

