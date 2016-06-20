#!/usr/bin/python
# coding: utf-8
#
# @file: media2image.py
# @date: 2016-06-16
# @brief:
# @detail:
#
#################################################################

''' 通过 ffmpeg，将视频文件转换为独立的图片文件 '''

import threading, os
import subprocess as sp
import sqlite3 as sq

def conv(f):
    ''' 如果是 /cygdrive/c/xxx，需要转换为 c:/xxx 格式'''
    if f[:11] == '/cygdrive/c':
        return 'c:' + f[11:]
    else:
        return f


class Media2Image(threading.Thread):
    def __init__(self, media_fname, size, rate, store):
        threading.Thread.__init__(self)
        self.__fname = conv(media_fname)
        self.__size = size
        self.__rate = rate
        self.__out = store
        self.__finished = False
        self.start()


    def run(self):
        command = [ "ffmpeg", 
            '-i', self.__fname,
            '-s', str(self.__size[0]) + 'x' + str(self.__size[1]),
            '-r', str(self.__rate),
            '-loglevel', '8',
            self.__out + '/' + 'img-%05d.jpg'
        ]

        print '============================================================'
        print command

        self.__proc = sp.Popen(command, stdout = sp.PIPE)
        self.__proc.communicate()
        self.__finished = True
        # FIXME 直接删除上传的视频文件 ...
        try:
            os.remove(self.__fname)
        except:
            pass
        self.prepare_db()


    def prepare_db(self):
        ''' 准备数据库 '''
        dbname = self.__out + '/../labels.db'  # 上一级目录 ..
        db = sq.connect(dbname)

        # 列出 mid 下所有 .jpg，添加到数据库中
        for fn in os.listdir(self.__out):
            x, ext = os.path.splitext(fn)
            if ext != '.jpg':
                continue
            cmd = 'insert into img values ("{}",-1,".",".")'.format(self.__out + '/' + fn)
            db.execute(cmd)

        db.commit()
        db.close()



    def is_finished(self):
        return self.__finished


    def stop(self):
        try:
            self.__proc.kill()
        except:
            pass

        self.join()


    def frames(self):
        ''' 返回已经分解的张数 ... '''
        n = os.listdir(self.__out)
        return len(n)



if __name__ == '__main__':
    import time, sys

    cf = '/cygdrive/c/store/0000000009'
    print conv(cf)
    sys.exit()

    mi = Media2Image("c:/Users/sunkw/Desktop/videos/51.mp4", (256, 256), 0.1, "c:/store/imgs")
    while not mi.is_finished():
        time.sleep(2.0)
        print mi.frames()

    mi.stop()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

