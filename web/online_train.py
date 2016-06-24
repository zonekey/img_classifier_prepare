#!/usr/bin/python
# coding: utf-8
#
# @file: online_train.py
# @date: 2016-06-24
# @brief:
# @detail:
#
#################################################################


from runproc import Running
import sys


''' 封装对 fine_tune 的调用，通过读取 stdout 得到训练的进度 ....
'''
class OnlineTrain(Running):
    def process_handler(self):
        while not self.need_quit():
            line = self.proc().stdout.readline()
            if not line:
                # 进程结束 ...
                break

            line = line.strip()
            if len(line) < 4:
                continue


            # FIXME: 有效记录为 'FT: .....'
            if line[0:4] == 'FT: ':
                self.save_info(line)



if __name__ == '__main__':
    import time

    dbname = '/home/sunkw/store/imgs/labels.db'

    ot = OnlineTrain()
    cmdline = ['python', 'fine_train.py', dbname]

    ot.start(cmdline)
    while ot.is_running():
        time.sleep(1.0)
        info = ot.get_last_info()
        if info:
            print info

    os.stop()





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

