#!/usr/bin/python
# coding: utf-8
#
# @file: img_mask.py
# @date: 2016-05-25
# @brief:
# @detail:
#
#################################################################

import cv2 as cv
import numpy as np
import os

''' 为当前目录下，所有img文件，设置多边形填充，方便屏蔽某个区域
'''

poly = [ (0,0), (130,0), (140, 64), (0, 100) ]
BACK_PIX = (127, 127, 127)

def is_imagefile(fname):
    imgs = ['.jpg', '.png']
    base, ext = os.path.splitext(fname)
    if ext in imgs:
        return True
    else:
        return False


def maskit(fname):
    m = cv.imread(fname)
    cv.fillPoly(m, [np.array(poly)], BACK_PIX)
    nfname = 'masked-' + fname
    cv.imwrite(nfname, m)


for fimgs in os.listdir('./'):
    if is_imagefile(fimgs):
        maskit(fimgs)





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

