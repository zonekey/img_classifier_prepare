#!/usr/bin/python
# coding: utf-8
#
# @file: server.py
# @date: 2016-06-12
# @brief: 基于 tornado，提供 RESTful 风格的分类接口
# @detail:
#
#################################################################

''' 分类接口分为三种：
        1. 单张图片：post image/jpg，立即返回分类描述
        2. 实时控制的分类：post media url，开始分类，当 put stop 时，结束分类，并且得到分类结果
        3. 批分类：post media urls, notify url，开始分类，当所有url分类结束后，通过 notify url 接口通知
'''


import tornado.web, tornado.ioloop, tornado.httpserver
import os, sys, time
import PIL
from PIL import Image
import cStringIO as StringIO
import cv2 as cv
import numpy as np
from classifier import Classifier
from session import Session
import threading
import json


def cb(opaque, rc):
    opaque.cb(rc)


class Application(tornado.web.Application):
    def __init__(self):
        self.__sessions = {} # 保存 sessions
        self.__batchs = {} # 保存批处理 ..
        self.__next_sid = 0
        self.__lock = threading.Lock()

        handlers = [
            (r'/', HelpHandler),
            
            (r'/pic', SinglePicture),
            
            (r'/stream', CreateSessionHandler),
            (r'/stream/([0-9]+)', DelSessionHandler),
            (r'/stream/([0-9]+)/(.*)', SessionHandler),

            (r'/batch', CreateBatchHandler),
            (r'/batch/([0-9]+)', DelBatchHandler),
            (r'/batch/([0-9]+)/(.*)', BatchHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


    def next_sid(self):
        self.__next_sid += 1
        return str(self.__next_sid)


    def cb(self, rc):
        #print rc
        pass


    def create_session(self, url, interval, topn = 3):
        global cb
        s = Session(cb, self, url=url, interval=interval, topn=topn)
        sid = self.next_sid()
        self.__sessions[sid] = s
        return sid


    def destory_session(self, sid):
        if sid in self.__sessions:
            s = self.__sessions[sid]
            s.close()
            del(self.__sessions[sid])
            return True
        else:
            return False


    def query_session(self, sid, begin, end):
        if sid not in self.__sessions:
            return None

        s = self.__sessions[sid]
        return s.results(begin, end)
    

    def is_running(self, sid):
        if sid not in self.__sessions:
            return False

        s = self.__sessions[sid]
        return s.is_running()



class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('help.html')


class CreateSessionHandler(tornado.web.RequestHandler):
    def post(self):
        j = json.loads(self.request.body)
        sid = self.application.create_session(url = j['url'], interval = j['interval'], topn = j['topn'])
        rx = { "error": 0, "sessionid": sid, 'host_clock': time.time()}
        self.finish(rx)


class DelSessionHandler(tornado.web.RequestHandler):
    def get(self, sid):
        self.redirect('/stream/' + sid + '/query')

    def delete(self, sid):
        rx = { "error": 0, "sessionid": sid }
        rc = self.application.destory_session(sid)
        if not rc:
            rx['error'] = -1
        self.finish(rx)


class SessionHandler(tornado.web.RequestHandler):
    def get(self, sid, cmd):
        if cmd == 'query':
            begin = float(self.get_query_argument('start', '0.0'))
            end = float(self.get_query_argument('stop', 'inf'))

            rcs = self.application.query_session(sid, begin, end)
            if rcs is None:
                self.finish('ERR: ' + sid + ', NO the session')
            else:
                rx = { 'state': '', 'results': [] }
                for rc in rcs:
                    descr = { 'stamp': rc['stamp'], \
                        'top1': rc['rc'][0][0], 'score1': rc['rc'][0][1], \
                        'top2': rc['rc'][1][0], 'score2': rc['rc'][1][1], \
                        'top3': rc['rc'][2][0], 'score3': rc['rc'][2][1], }
                    rx['results'].append(descr)
    
                if self.application.is_running(sid):
                    rx['state'] = 'running'
                else:
                    rx['state'] = 'stopped'
                self.finish(rx)
        else:
            self.finish('ERR: ' + sid + ', unknown cmd:' + cmd)


class CreateBatchHandler(tornado.web.RequestHandler):
    def post(self):
        # TODO: 
        self.finish('NOT impl')


class DelBatchHandler(tornado.web.RequestHandler):
    def delete(self, bid):
        # TODO:
        self.finish('NOT impl')


    def get(self, bid):
        self.redirect('/batch/' + bid + '/query')


class BatchHandler(tornado.web.RequestHandler):
    def get(self, bid, cmd):
        # TODO:
        self.finish('NOT impl')
        


class SinglePicture(tornado.web.RequestHandler):
    def post(self):
        '''  curl --request POST -data-binary "@fname.jpg" --header "Content-Type: image/jpg"  http://localhost:8899/pic
             将返回分类结果 ...
        '''
        global cf

        body = self.request.body
        try:
            img = Image.open(StringIO.StringIO(body))
            img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
            pred = cf.predicate(img)
            info = ""
            for i in range(0, 3):
                info += pred[i][1] + ', score:' + str(pred[i][2]) + '\n'
            self.finish(info)
        except Exception as e:
            print e
            self.finish(str(e))



# 仅仅用于单幅图片的分类，对于 url，还是启动独立的工作进程搞吧 ..
cf = Classifier('../models/deploy.prototxt',
    '../models/pretrained.caffemodel',
    '../models/mean.binaryproto',
    '../models/labels.txt')


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8899)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

