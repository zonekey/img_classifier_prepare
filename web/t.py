#!/usr/bin/python
# coding: utf-8
#
# @file: t.py
# @date: 2016-06-13
# @brief: 模拟实现老刘的 c++ 版本
# @detail:
#
#################################################################

import time, sys, os
from video_cap import VideoCap
from classifier import Classifier
import locale

url = ''
interval = 3.0
topn = 3


try:
    url = sys.args[1]
    interval = float(sys.args[2])
    topn = int(sys.args[3])
except:
    print 'usage', sys.args[0], ' <url> <interval> <topn>'
    sys.exit()


print 'url', url
print 'interval', interval
print 'topn', topn

stamp_begin = -1.0

cf = Classifier('../models/deploy.prototxt',
    '../models/pretrained.caffemodel',
    '../models/mean.binaryproto',
    '../models/labels.txt')
vc = VideoCap(url, (256, 256), "1/3")


curr_encoding = locale.getdefaultlocale()[1]

def cb_image(image):
    global cf, quit, stamp_begin

    if image == None:
        quit = True
        return
   
    if stamp_begin < 0.0:
        stamp_begin = time.time()

    pred = cf.predicate(image)
    stamp = time.time() - stamp_begin

    print stamp, pr(pred[0][1]), pred[0][2], pr(pred[1][1]), pred[1][2], pr(pred[2][1]), pred[2][2]


def pr(s):
    global curr_encoding
    return s.decode('UTF-8').encode(curr_encoding)


quit = False
vc.start(cb_image)

while not quit:
    time.sleep(1.0)

vc.stop()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

