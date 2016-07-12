#!/usr/bin/python
# coding: utf-8
#
# @file: runproc.py
# @date: 2016-06-24
# @brief:
# @detail:
#
#################################################################

''' 封装外部进程的执行 ....'''


import subprocess as sp
import threading, time, os, sys


class Running(threading.Thread):
    def start(self, cmdline):
        ''' cmdline 为 []，包含命令行参数 '''
        if len(cmdline) == 0:
            raise Exception('Running', 'start: cmdline is empty!!!!')

        self.__running = threading.Event()
        self.__cmdline = cmdline
        self.__info = []    # 
        self.__quit = False
        self.__proc = None
        self.__updated = False
        threading.Thread.start(self)
        self.__running.wait()


    def stop(self):
        self.__quit = True
        self.__proc.terminate()
        self.join()


    def is_running(self):
        return self.proc is not None


    def run(self):
        self.__running.set()
        self.__proc = sp.Popen(self.__cmdline, stdout = sp.PIPE, stderr = sp.PIPE)
        self.process_handler()


    def process_handler(self):
        # 派生类实现 ...
        raise Exception('Running', 'process_handler')


    def proc(self):
        return self.__proc


    def need_quit(self):
        return self.__quit


    def save_info(self, item, stamp = None):
        if stamp is None:
            self.__info.append({'stamp':time.time(), 'item':item})
        else:
            self.__info.append({'stamp':stamp, 'item':item})
        self.__updated = True

    def get_info(self):
        return self.__info


    def get_last_info(self):
        if len(self.__info) == 0:
            return None
        else:
            return self.__info[-1]['item']





if __name__ == '__main__':
    class M(Running):
        def process_handler(self):
            pipe = self.proc()
            line = pipe.stdout.readline()
            while line:
                line = line.strip()
                print line
                if self.need_quit():
                    break
                line = pipe.stdout.readline()


    cmdline = ['ls', '-l']
    r = M()
    r.start(cmdline)
    r.stop()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

