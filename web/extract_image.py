#!/usr/bin/python
# coding: utf-8
#
# @file: extract_image.py
# @date: 2016-06-16
# @brief:
# @detail:
#
#################################################################


import threading
import subprocess as sp


''' 利用 ffmpeg 分解图片到指定目录中 '''
class ExtractImages(threading.Thread):
    def __init__(self, media_fname, size, rate, store):
        threading.Thread.__init__(self)
        self.__fname = media_fname
        self.__size = size
        self.__rate = rate
        self.__out = store


    def run(self):
        command = [ "ffmpeg", 
            '-i', self.__fname,
            '-s', str(self.__size[0]) + 'x' + str(self.__size[1]),
            '-r', str(self.__rate),
            '-loglevel', '8',
            self.__out + '/' + 'img-%05d.jpg'
        ]

        self.__proc = sp.Popen(command, stdout = sp.PIPE)

        quit = False
        while not quit:
            line = self.__proc.stdout.readline()
            if line == None:
                break




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

