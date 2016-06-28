#!/usr/bin/python
# coding: utf-8

import tornado.web, tornado.ioloop, tornado.httpserver
import json
from training import TrainApiHandler, TrainShowingHandler

cfg = json.load('./cfg/config.json')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/train/showing', TrainShowingHandler),
            (r'/train/api/(.+)', TrainApiHandler),
        ]
        tornado.web.Application.__init__(self, handlers=handlers, cookie_secret="abcd")

        self.training = None # 对应 online_train.py
        self.who = None      # 启动训练的登录名字


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
