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


caffe.set_mode_cpu()    # in windows, only CPU mode supported


class Classifier:
    def __init__(self, deploy, pretrained, mean, labels):
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
        prediction = self.__net.predict([image])
        print 'prediction shape:', prediction[0].shape
        print 'predicted class:', prediction[0].argmax()
        return prediction


    def load_labels(self, fname):
        ''' 从 fname 中加载标签解释 '''
        labels = []
        with open(fname, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) > 1:
                    labels.append(line)


    def convert(self, mean_fname):
        blob = caffe.proto.caffe_pb2.BlobProto()
        data = open(mean_fname, 'rb').read()
        blob.ParseFromString(data)
        return np.array(caffe.io.blobproto_to_array(blob))[0]



if __name__ == '__main__':
    import matplotlib.pyplot as plt

    image = caffe.io.load_image('1.jpg')
    plt.imshow(image)

    cf = Classifier('../models/deploy.prototxt',
            '../models/pretrained.caffemodel',
            '../models/mean.binaryproto',
            '../models/labels.txt')

    pred = cf.predicate(image)
    plt.plot(pred[0])

    plt.show()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
