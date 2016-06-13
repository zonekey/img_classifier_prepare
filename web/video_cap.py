#!/usr/bin/python
# coding: utf-8
#
# @file: video_cap.py
# @date: 2016-06-09
# @brief: 利用 ffmpeg image2pipe 格式，将 url 解码到 pipe，通过 pipe.stdout.read，
#         将数据保存到 np array 中
#         需要支持提前结束 ...
# @detail:
#
#################################################################

import numpy as np
import subprocess as sp
import threading
import cv2

class VideoCap(threading.Thread):
    def __init__(self, input_url, size, rate):
        threading.Thread.__init__(self)
        self.__url = input_url
        self.__size = size  # (width, height)
        self.__rate = rate
        self.__quit = threading.Event()

    def start(self, callback = None):
        self.__quit.clear()
        self.__callback = callback
        threading.Thread.start(self)


    def stop(self):
        ''' 发出 quit 通知，然后 join 工作线程 '''
        self.__quit.set()
        threading.Thread.join(self)


    def check_quit(self):
        ''' 检查是否收到 quit 命令 '''
        return self.__quit.wait(0.01)


    def run(self):
        command = ['ffmpeg', 
                  '-v', '-1',
                  '-i', self.__url, 
                  '-s', str(self.__size[0]) + 'x' + str(self.__size[1]),
                  '-r', self.__rate, 
                  '-f', 'image2pipe',
                  '-pix_fmt', 'bgr24',
                  '-vcodec', 'rawvideo', 
                  '-']
        pipe = sp.Popen(command, stdout=sp.PIPE)

        quit = False;
        while not quit:
            raw_image = pipe.stdout.read(self.__size[0] * self.__size[1] * 3) # BGR24
            if not raw_image:
                # 播放结束?
                if self.__callback:
                    self.__callback(None)
                break

            image = np.fromstring(raw_image, dtype = 'uint8')
            image = image.reshape((self.__size[1], self.__size[0], 3))
    
            if self.__callback:
                self.__callback(image)

            quit = self.check_quit()
        



if __name__ == '__main__':
    import time
    
    vc = VideoCap("c:/Users/sunkw/Desktop/videos/51.mp4", (256, 256), "25")
    
    cnt = 0
    quit = False

    def cb(image):
        global cnt, quit

        if image is None:
            print 'End....'
            quit = True
        else:
            cnt += 1
    
    vc.start(cb)
    
    while not quit:
        time.sleep(1.0)
    
    print cnt, 'images saved!'




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

