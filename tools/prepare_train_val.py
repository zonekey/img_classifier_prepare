#!/usr/bin/python
# coding: utf-8
#
# @file: prepare_train_val.py
# @date: 2016-05-23
# @brief:
# @detail:
#
#################################################################

''' 根据子目录，生成 train.txt val.txt labels.txt 文件，方便训练
'''

import os, random

reserved = [ 'skipped', 'confused' ]
catalogs = []


def is_imagefile(fname):
    imgs = ['.jpg', '.png']
    base, ext = os.path.splitext(fname)
    if ext in imgs:
        return True
    else:
        return False


def one_catalog(subdir, n):
    ''' 生成 train_X.txt 保存 subdir 下的 80% 的文件，
        生成 val_X.txt 保存 subdir 下其他的 20% 的文件
    '''
    train_f = open("train_" + str(n) + ".txt", 'w')
    val_f = open("val_" + str(n) + ".txt", 'w')

    imgs = []
    for fn in os.listdir(subdir):
        if os.path.isdir(fn):
            continue

        fname = subdir + '/' + fn;
        if is_imagefile(fname):
            imgs.append(fname)

    random.shuffle(imgs)
    for i in range(0, len(imgs)):
        if i % 5 == 0:
           val_f.write(imgs[i] + ' ' + str(n) + '\n')
        else:
           train_f.write(imgs[i] + ' ' + str(n) + '\n')

    train_f.close()
    val_f.close()
        

for n in os.listdir('./'):
    catalog = str(n)
    if catalog in reserved:
        continue

    if os.path.isdir(catalog):
        catalogs.append(catalog)

l = open('labels.txt', 'w')
n = 0
for catalog in catalogs:
    one_catalog(catalog, n)
    l.write(str(n) + ' ' + catalog + '\n')
    n = n + 1
l.close()

# 合并 train_X.txt 到 train.txt
t = open('train.txt', 'w')
v = open('val.txt', 'w')
for i in range(0, n):
    ft = open('train_' + str(i) + '.txt', 'r')
    for line in ft:
        t.write(line)
    ft.close()

    fv = open('val_' + str(i) + '.txt', 'r')
    for line in fv:
        v.write(line)
    fv.close()
t.close()
v.close()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

