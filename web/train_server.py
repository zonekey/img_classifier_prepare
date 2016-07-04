#!/usr/bin/python
# coding: utf-8

import tornado.web, tornado.ioloop, tornado.httpserver
import json
from training import TrainApiHandler, TrainShowingHandler

def loadcfg(fname):
    try:
        with open(fname) as f:
            s = f.read()
            return json.loads(s)
    except:
        return {}


cfg = loadcfg('./cfg/config1.json')
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/train/showing', TrainShowingHandler),
            (r'/train/api/(.+)', TrainApiHandler),
        ]
        tornado.web.Application.__init__(self, handlers=handlers, cookie_secret="abcd")

        self.training = None # 对应 online_train.py
        self.who = None      # 启动训练的登录名字
        self.__high_acc = -1.0
        self.__high_num = 0


    def save_curr_iternum_accuracy(self, num, acc):
        if acc > self.__high_acc:
            self.__high_acc = acc
            self.__high_num = num

    def high_num_acc(self):
        return (self.__high_num % 1000, self.__high_acc)



def main():
    httpserver = tornado.httpserver.HTTPServer(Application())
    port = 8898
    if 'train_server_port' in cfg:
        port = cfg['train_server_port']
    httpserver.listen(port)
    print 'running traing server on port:', port
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
