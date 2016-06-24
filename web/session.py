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
import locale, time
from runproc import Running


curr_encoding = locale.getdefaultlocale()[1]  # UTF-8 或者 gbk/cp936 ...


class Session(threading.Thread):
    def __init__(self, cb, opaque, sid, **kwargs):
        threading.Thread.__init__(self)
        self.__cb = cb      # 回调函数，当收到一条分析结果 ...
        self.__sid = sid
        self.__begin = time.time()
        self.__opaque = opaque
        self.__result = []  # 保存每帧的分析结果 { [ {'stamp': xxx, 'cf': [ (xx, 0.8766), (yy, 0.1192) ... ]}, {'stamp': ....} ] }
        self.__proc = None
        self.__started = threading.Event()
        self.__cfg = {}
        self.__lock = threading.Lock()
        self.__notify_url = None
        for key in kwargs:
            self.__cfg[key] = kwargs[key]
            if key == 'notify_url':
                self.__notify_url = kwargs[key]

        self.start()
        self.__started.wait()


    def is_running(self):
        return self.__proc is not None


    def descr(self):
        # 返回描述
        last_stamp = -1
        if len(self.__result) > 0:
            last_stamp = self.__result[-1]['stamp']

        return {
            "sid": self.__sid,
            "begin": self.__begin,
            "running": self.is_running(),
            "boot_cfg": self.__cfg,
            "cf_images": len(self.__result),
            "last_stamp": last_stamp,
        }


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
            print 'ERR: can\'t start:', command
            return

        quit = False
        while not quit:
            line = pipe.stdout.readline()
            if not line:
                # FIXME: 进程结束，仅仅此种情况下，主动通知 ..
                if self.__notify_url:
                    notify()
                break

            line = line.strip()
            if len(line) < 10:
                continue

            if line[0:3] == 'CR:':
                # line 格式：CR: stamp top1 score1 top2 score2 top3 score3
                ss = line.split()
                if len(ss) == 8:
                    rc = { 'stamp': float(ss[1]), 
                           'cf': [
                                    { 'label': int(ss[2]), 'score': float(ss[3]) },
                                    { 'label': int(ss[4]), 'score': float(ss[5]) },
                                    { 'label': int(ss[6]), 'score': float(ss[7]) },
                           ] 
                    }

                    self.__lock.acquire()
                    self.__result.append(rc)
                    self.__lock.release()

                    if self.__cb:
                        self.__cb(self.__opaque, rc)

        self.__proc = None


    def notify(self):
        # TODO: 任务已经完成，主动通知到 notify_url
        pass


    def rp(self, s):
        # 从当前编码转换到 utf-8
        return s.decode(curr_encoding).encode('UTF-8')


    def build_cmd(self):
        ''' 从 cfg 构造命令行参数, 一般拥有 url, interval '''

        # TODO: 修改为调用老刘的c++版本
        command = [ 'python', 't.py', self.__cfg['url'], str(self.__cfg['interval']) ]
        return command


    def close(self):
        if self.__proc:
            try:
                # proc 可能已经结束了 ..
                self.__proc.terminate()
            except Exception as e:
                print e
        self.join()


    def results(self, begin, end = sys.float_info.max):
        ''' 返回 begin 到 end 之间的时间戳 '''
        rcs = []
        self.__lock.acquire()
        for rc in self.__result:
            if rc['stamp'] >= begin and rc['stamp'] < end:
                rcs.append(rc)
        self.__lock.release()
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

