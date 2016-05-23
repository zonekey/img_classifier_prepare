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
    	在 64x64 的白底，左上角画 黑矩形，随机偏移几个像素，大小也随机差几个像素，生成 N 张样本
		作为训练集合。
		测试集合，将“黑矩形”放到右下角，如果预测成功，则说明有可能支持“空间映射” ...
'''

N = 100
WIDTH, HEIGHT = 64, 64
BACK_PIX = 128

os.mkdir('rect')
os.mkdir('circle')

for i in range(0, N):
	m = np.zeros((HEIGHT, WIDTH, 1), np.uint8)
	m.fill(BACK_PIX)
	# 画矩形
	dx, dy = 5 * random.random(), 5 * random.random()
	dw, dh = 3 * random.random(), 3 * random.random()
	tl = (0 + int(dx), 0 + int(dy))
	br = (20 + int(dw), 20 + int(dh))
	cv.rectangle(m, tl, br, 0, -1)
	fname = 'rect/rect-%03d.jpg' % i
	cv.imwrite(fname, m)

    # 画圆
	m.fill(BACK_PIX)
	center = (20 + int(dx), 20 + int(dy))
	radius = 10 + int(dw)
	cv.circle(m, center, radius, 0, -1)
	fname = 'circle/circ-%03d.jpg' % i
	cv.imwrite(fname, m)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

