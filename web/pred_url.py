#!/usr/bin/python
# coding: utf-8
#
# @file: pred_url.py
# @date: 2016-06-12
# @brief: 预测 url
# @detail:
#
#################################################################


from video_cap import VideoCap
from classifier import Classifier
import sys, time
import cv2


if __name__ == '__main__':
    url = sys.argv[1]

    cf = Classifier('../models/deploy.prototxt',
            '../models/pretrained.caffemodel',
            '../models/mean.binaryproto',
            '../models/labels.txt')

    quit = False

    def cb_image(img):
        global quit, cf

        if img is None:
            print 'end'
            quit = True
        else:
            pred = cf.predicate(img)
            f = cv2.resize(img, (480, 270))
            cv2.imshow('show', f)
            key = cv2.waitKey(1)
            print pred[0][1].decode('utf-8').encode('gbk') + ' score:', pred[0][2]


    vc = VideoCap(url, (256, 256), "1/3")
    vc.start(cb_image)

    while not quit:
        time.sleep(1.0)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

