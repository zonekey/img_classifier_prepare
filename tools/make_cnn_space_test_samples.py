#!/usr/bin/python
# coding: utf-8
#
# @file: make_cnn_space_test_samples.py
# @date: 2016-05-23
# @brief:
# @detail:
#
#################################################################

import cv2 as cv
import numpy as np
import random, os

''' 为了验证 CNN 能否支持空间变化的特性，做如下测试: 
        在 256x256 的纯色底，左上角画 黑矩形，随机偏移几个像素，大小也随机差几个像素，生成 N 张样本
        作为训练集合。
        测试集合，将“黑矩形”放到右下角，如果预测成功，则说明有可能支持“空间映射” ...
'''

N = 2000
WIDTH, HEIGHT = 256, 256
BACK_PIX = 255

try:
    os.mkdir('rect')
except:
    pass

try:
    os.mkdir('circle')
except:
    pass

try:
    os.mkdir('triangle')
except:
    pass

for i in range(0, N):
    m = np.zeros((HEIGHT, WIDTH, 1), np.uint8)
    dx, dy = 10 * random.random(), 10 * random.random()
    dw, dh = 10 * random.random(), 10 * random.random()

    # 画矩形
    m.fill(BACK_PIX)
    tl = (0 + int(dx), 0 + int(dy))
    br = (80 + int(dw), 80 + int(dh))
    cv.rectangle(m, tl, br, 0, 3)
    fname = 'rect/rect-%04d.jpg' % i
    cv.imwrite(fname, m)

    # 画圆
    m.fill(BACK_PIX)
    center = (80 + int(dx), 80 + int(dy))
    radius = 30 + int(dw)
    cv.circle(m, center, radius, 0, 3)
    fname = 'circle/circ-%04d.jpg' % i
    cv.imwrite(fname, m)

    # 画三角
    m.fill(BACK_PIX) 
    v1 = (60 + int(dx), 50 + int(dy))
    v2 = (30 + int(dy), 100 + int(dx))
    v3 = (90 + int(dx), 100 + int(dy))
    v = [v1, v2, v3]
    nv = np.array(v, np.int32)
    cv.polylines(m, [nv], True, 0, 3);
    fname = 'triangle/tri-%04d.jpg' % i
    cv.imwrite(fname, m)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

