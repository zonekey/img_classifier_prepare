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
import urllib2


''' 封装对 fine_tune 的调用，通过读取 stdout 得到训练的进度 ....
'''
class OnlineTrain(Running):
    def __init__(self):
        self.state = 'norunning'
        Running.__init__(self)


    def process_handler(self):
        self.state = 'training'

        while not self.need_quit():
            line = self.proc().stdout.readline()
            if not line:
                # 进程结束 ...
                self.state = 'done' # 训练结束
                print 'pipe end!'
                break

            line = line.strip()
            if len(line) < 4:
                continue
    
            # FIXME: 有效记录为 'FT: .....'
            if line[0:4] == 'FT: ':
                '''
                    FT: stamp iter_num train_cnt test_cnt accuracy 
                '''
                ss = line.split(' ')
                if len(ss) == 6:
                    d = {'time': float(ss[1]),
                        'iter_num': int(ss[2]),
                        'train_cnt': int(ss[3]),
                        'test_cnt': int(ss[4]),
                        'accuracy': float(ss[5]),
                    }
                    print 'OnlineTrain: save', d
                    self.save_info(d)
        print 'OnlineTrain thread terminated!!!'
        urllib2.urlopen('http://172.16.1.60:8812/fine_tune/info?complete')




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

