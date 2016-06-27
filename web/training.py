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
            self.redirect('/login?loc=' + self.request.uri)
            return

        if cmd == 'start_train':
            return self.start_train()
        if cmd == 'stop_train':
            return self.stop_train()

    
    def start_train(self):
        ''' 启动训练进程,
            
            返回
            {
                'result': 'ok|error',   正常启动，或者已经启动，或者样本数太少？
                'info': 'xxx',
            }
        '''
        rx = { 'result': 'ok', 'info': '' }

        if self.application.training:
            rx['result'] = 'error'
            rx['info'] = 'other training instance exist!'
            self.finish(rx)
            return

        dbname = '/home/sunkw/store/imgs/labels.db'
        cmd = ['python', 'fine_tune.py', dbname]
            
        ot = OnlineTrain()
        ot.start(cmd)
        self.application.training = ot
        self.application.training_user = self.current_user
        rx['info'] = 'started'
        self.finish(rx)


    def stop_train(self):
        ''' 终止，只能停止自己的训练 ... 

            返回
            {
                'result': 'ok|error',
                'info': 'xxx'
            }
    
        '''
        rx = { 'result': 'ok', 'info': '' }

        if not self.application.training:
            rx['result'] = 'error'
            rx['info'] = 'NO training!'
            self.finish(rx)
            return

        if self.current_user != self.application.training_user:
            rx['result'] = 'error'
            rx['info'] = 'NOT your training session!'
            self.finish(rx)
            return

        ot = self.application.training
        ot.stop()
        self.application.training = None
        self.application.training_user = None
        rx['info'] = 'stopped'
        self.finish(rx)


    def get_progress(self):
        ''' 返回训练进度信息，使用长轮询 ??? 

            不管是否是其他人的，都可以查询

            希望能够获取如下信息 ...

            {
                'status': "done|training|norunning",    进程执行状态
                'time': 136.433,                    启动训练的时间
                'iter_num': 2000,                   训练迭代次数
                'test_cnt': 1500,                   测试集合的样本数
                'train_cnt': 6000,                  训练样本数
                'accuracy': 0.83,                   最新的测试准确度
                'elapsed': 3600,                    预计训练完成需要的时间 ...
            }

        '''
        rx = {'status': 'norunning' }
        if not self.application.training:
            self.finish(rx)
            return

        ot = self.application.training
        info = ot.get_last_info()

        







# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

