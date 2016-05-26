#!/usr/bin/python
# coding: utf-8
#
# @file: make_catalog_dirs.py
# @date: 2016-05-26
# @brief:
# @detail:
#
#################################################################

''' 根据 labels.txt 创建子目录
'''

import os

f = open('labels.txt', 'r')
for line in f:
    line = line.strip()
    try:
        os.mkdir(line)
        print 'create subdir', line
    except:
        pass
f.close()





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

