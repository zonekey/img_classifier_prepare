#!/usr/bin/python
# coding: utf-8
#
# @file: classifier.py
# @date: 2016-06-09
# @brief:
# @detail:
#
#################################################################

import caffe
import numpy as np
import cv2
import sys, codecs



class Classifier:
    def __init__(self, deploy, pretrained, mean, labels, gpu = False):
        if gpu:
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()    # in windows, only CPU mode supported

        self.__labels = self.load_labels(labels);
        mean_ar = self.convert(mean)
        print mean_ar.shape
        
        self.__net = caffe.Classifier(deploy, pretrained,
                mean = mean_ar.mean(1).mean(1),
                channel_swap = (2, 1, 0), 
                raw_scale = 255,
                image_dims = (256, 256))


    def predicate(self, image):
        ''' 输入图像，输出前 N 类预测结果，以及可信度
             [ ( 3, '单人-讲台区-看-学生区', 0.933), (5, '单人-讲桌-看-学生区', 0.03) ... ]
        '''
        prediction = self.__net.predict([image], False) # 不使用crop/mirror均值
        return self.sort_preds(prediction[0])


    def sort_preds(self, scores):
        ''' scores 为 []，为每类的可信度 '''
        cs = {}
        c = 0
        for scors in scores:
            cs[c] = scors
            c += 1
        # cs 根据 value 从大到小排序
        cs = sorted(cs.iteritems(), key = lambda d:d[1], reverse = True)
        preds = []
        for c in cs:
            if self.__labels and len(self.__labels) > c[0]:
                label = self.__labels[c[0]]
            else:
                label = ""
            preds.append((c[0], label, c[1]))
        return preds


    def load_labels(self, fname):
        ''' 从 fname 中加载标签解释 '''
        labels = []
        with open(fname, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) > 1:
                    labels.append(line)
        return labels


    def get_labels(self):
        return self.__labels


    def convert(self, mean_fname):
        blob = caffe.proto.caffe_pb2.BlobProto()
        data = open(mean_fname, 'rb').read()
        blob.ParseFromString(data)
        return np.array(caffe.io.blobproto_to_array(blob))[0]



if __name__ == '__main__':
    cf = Classifier('../models/deploy.prototxt',
            '../models/pretrained.caffemodel',
            '../models/mean.binaryproto',
            '../models/labels.txt')

    image = caffe.io.load_image('1.jpg') # 加载图片 ..
    pred = cf.predicate(image) # 预测

    # print pred
    print 'for image:'
    for i in range(0, 3):
        print pred[i][1].decode('utf-8').encode('gbk'), pred[i][2]


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
