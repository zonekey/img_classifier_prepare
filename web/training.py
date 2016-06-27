#!/usr/bin/python
# coding: utf-8
#
# @file: training.py
# @date: 2016-06-24
# @brief:
# @detail:
#
#################################################################

''' 在线训练部分，放到独立的py中吧 ...
'''

from baserequest import BaseRequest
from online_train import OnlineTrain


class TrainShowingHandler(BaseRequest):
    def get(self):
        ''' FIXME: 如果没有登录，直接点开这个url，返回 404 错误 :) '''
        if not self.current_user:
            self.clear()
            self.set_status(404)
            self.finish('<html><body>谁？？</body></html>')
        else:
            self.render('train_showing.html')


class TrainApiHandler(BaseRequest):
    def get(self, cmd):
        if not self.current_user:
            return self.redirect('/login?loc=' + self.request.uri)
            return

        if cmd == 'start_train':
            return self.start_train()
        if cmd == 'stop_train':
            return self.stop_train()

    
    def start_train(self):
        ''' 启动训练进程 '''
        dbname = '/home/sunkw/store/imgs/labels.db'
        cmd = ['python', 'fine_tune.py', dbname]
            
        ot = OnlineTrain()
        ot.start(cmd)


    def stop_train(self):
        ''' 终止 ... '''
        pass


    def get_progress(self):
        ''' 返回训练进度信息，使用长轮询 ??? 

            希望能够获取如下信息 ...

            {
                'status': "done|training|error",    进程执行状态
                'time': 136.433,                    启动训练的时间
                'iter_num': 2000,                   训练迭代次数
                'test_cnt': 1500,                   测试集合的样本数
                'train_cnt': 6000,                  训练样本数
                'accuracy': 0.83,                   最新的测试准确度
                'elapsed': 3600,                    预计训练完成需要的时间 ...
            }

        '''

        pass






# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

