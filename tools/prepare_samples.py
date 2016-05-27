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

import os, random, json, sys
import codecs

reserved = [ 'skipped', 'confused' ]
catalogs = []


def is_imagefile(fname):
    imgs = ['.jpg', '.png']
    base, ext = os.path.splitext(fname)
    if ext in imgs:
        return True
    else:
        return False


def load_catalogs(fname):
    with open(fname, 'r') as f:
        s = json.load(f)
        return s



testing = True

try:
    if sys.argv[1] == 'train_val':
        testing = False
except:
    pass

if testing:
    print 'INFO: gather testing samples....'
else:
    print 'INFO: prepare train & val samples ...'


cfg = load_catalogs('catalogs.json')
root = cfg['root']
catalogs = cfg['catalogs']

print 'INFO: there are %d catalogs' % len(catalogs)
print 'INFO: root path:', root


def one_subdir(sub):
    imgs = []
    for fn in os.listdir(sub):
        if os.path.isfile(sub + '/' + fn) and is_imagefile(fn):
            imgs.append(sub + '/' + fn)
    return imgs


def one_catalog2(path, c):
    label = str(c['label'])
    if testing:
        t = codecs.open('test_' + label, 'w', encoding='utf-8')
    else:
        t = codecs.open('train_' + label, 'w', encoding='utf-8')
        v = codecs.open('val_' + label, 'w', encoding='utf-8')

    imgs = []
    for fn in os.listdir(path):
        if not os.path.isdir(path + '/' + fn):
            continue

        if fn in reserved:
            continue

        if fn in c['titles']:
            subimgs = one_subdir(path + '/' + fn)
            for sfn in subimgs:
                imgs.append(sfn)

    if testing:
        for fn in imgs:
            x = fn + ' ' + label;
            t.write(x + '\n')
        t.close()
    else:
        for i in range(0, len(imgs)):
            if i % 5 == 0:
                v.write(fn + ' ' + label + '\n')
            else:
                t.write(fn + ' ' + label + '\n')
        t.close()
        v.close()


for c in catalogs:
    one_catalog2(root, c)

# 合并 train_X.txt 到 train.txt
if testing:
    t = open('test.txt', 'w')
    for i in range(0, len(catalogs)):
        with open('test_' + str(i), 'r') as f:
            for line in f:
                t.write(line)
        os.remove('test_' + str(i))
    t.close()
else:
    t = open('train.txt', 'w')
    v = open('val.txt', 'w')
    for i in range(0, len(catalogs)):
        ft = open('train_' + str(i), 'r')
        for line in ft:
            t.write(line)
        ft.close()
        os.remove('train_' + str(i))

        fv = open('val_' + str(i), 'r')
        for line in fv:
            v.write(line)
        fv.close()
        os.remove('val_' + str(i))
    t.close()
    v.close()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

