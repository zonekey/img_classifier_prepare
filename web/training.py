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
        pass


    def stop_train(self):
        pass






# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

