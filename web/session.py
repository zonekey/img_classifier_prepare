#!/usr/bin/python
# coding: utf-8
#
# @file: session.py
# @date: 2016-06-13
# @brief:
# @detail:
#
#################################################################

''' 对应一个实时受控任务, 通过 pipe, mmap 进行交互 
'''


import subprocess as sp
import sys, os, threading


class Session(threading.Thread):
    def __init__(self, cb, opaque, **kwargs):
        threading.Thread.__init__(self)
        self.__cb = cb      # 回调函数，当收到一条分析结果 ...
        self.__opaque = opaque
        self.__result = []  # 保存每帧的分析结果 { [ {'stamp': xxx, 'rc': [ ('XXXX', 0.8766), ('YYYY', 0.1192) ... ]}, {'stamp': ....} ] }
        self.__proc = None
        self.__started = threading.Event()
        self.__cfg = {}
        for key in kwargs:
            self.__cfg[key] = kwargs[key]
        self.start()
        self.__started.wait()


    def is_running(self):
        return self.__proc is not None


    def run(self):
        ''' subprocess 启动进程，通过 pipe 接收每帧的分析结果 '''
        command = self.build_cmd()

        try:
            pipe = sp.Popen(command, stdout = sp.PIPE)
            self.__proc = pipe
        except Exception as e:
            print e
            self.__proc = None

        self.__started.set()
        if not self.__proc:
            return

        print 'working thread running'

        quit = False
        while not quit:
            line = pipe.stdout.readline()
            if not line:
                self.__proc = None
                break       # 进程结束 ..

            line = line.strip()

            # line 格式：stamp top1 score1 top2 score2 top3 score3
            ss = line.split()
            if len(ss) == 7:
                rc = { 'stamp': float(ss[0]), 
                       'rc': [
                               ( ss[1], float(ss[2])),
                               ( ss[3], float(ss[4])),
                               ( ss[5], float(ss[6]))
                       ] 
                }
                self.__result.append(rc)
                if self.__cb:
                    self.__cb(self.__opaque, rc)
        print 'working thread end'


    def build_cmd(self):
        ''' 从 cfg 构造命令行参数 '''
        command = [ 'python', 't.py' ]
        return command


    def close(self):
        if self.__proc:
            try:
                # proc 可能已经结束了 ..
                self.__proc.terminate()
            except Exception as e:
                print e
        self.join()
        print 'session closed'


    def results(self, begin, end = sys.float_info.max):
        ''' 返回 begin 到 end 之间的时间戳 '''
        rcs = []
        for rc in self.__result:
            if rc['stamp'] >= begin and rc['stamp'] < end:
                rcs.append(rc)
        return rcs



if __name__ == '__main__':
    def cb(opaque, rc):
        print rc


    import time
    session = Session(cb, None)
    time.sleep(3.0)
    session.close()

    print session.results(0.0009, 0.001)




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

