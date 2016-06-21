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
from media2image import Media2Image
import threading
import json
import caffe
from usertask import UserTask


lock = threading.Lock()


def cb(opaque, rc):
    opaque.cb(rc)


class Application(tornado.web.Application):
    def __init__(self):
        self.__sessions = {} # 保存 sessions
        self.__batchs = {} # 保存批处理 ..
        self.__mis = {} # 保存正在进行的转换进程 ..
        self.__next_sid = 0
        self.__lock = threading.Lock()

        if sys.platform.find('win32') == 0:
            self.__mis_root = "c:/store/imgs" # 存储转换后的图片 ..
            cmd_path = self.__mis_root.replace('/', '\\')
            os.system('mkdir ' + cmd_path) # cmd.exe 需要 
        else:
            home = os.getenv('HOME')
            self.__mis_root = home + '/store/imgs'
            os.system('mkdir -p ' + self.__mis_root)
        self.__users = {}



        # 准备数据库 ...
        self.prepare_db()


        handlers = [
            (r'/', HelpHandler),
            (r'/login', LoginHandler),
            
            (r'/pic', SinglePicture),
            
            (r'/stream', CreateSessionHandler),
            (r'/stream/([0-9]+)', DelSessionHandler),
            (r'/stream/([0-9]+)/(.*)', SessionHandler),

            (r'/batch', CreateBatchHandler),
            (r'/batch/([0-9]+)', DelBatchHandler),
            (r'/batch/([0-9]+)/(.*)', BatchHandler),


            (r'/retrain', RetrainIndexHandler),
            (r'/retrain/media2image', RetrainMedia2ImageHandler),
            (r'/retrain/cf', RetrainShowingHandler),
            (r'/retrain/api/next', RetrainNextImageHandler),    # 获取下一张图片的分类结果 ..
            (r'/retrain/api/confirm', RetrainImageCfHandler),   # 确认分类结果，PUT
            (r'/retrain/api/cancel', RetrainImageCancelHandler),  # 撤销
            (r'/retrain/api/skip', RetrainImageSkipHandler), # 跳过

            (r'/imgs/(.*)', NoCacheHandler, {'path': self.__mis_root } ), # 图片文件..

            (r'/get_labels', GetClassifierLabelsHandler),  # 返回所有的标签，json
        ]
        tornado.web.Application.__init__(self, handlers, cookie_secret="abcd")


    def prepare_db(self):
        ''' 在 self.__mis_root 下创建 labels.db，格式为：
                fname: 完整的文件路径名
                pred_label: int
                label: int
                title: label 的说明
                who: 登录者
        '''
        import sqlite3 as sq
        conn = sq.connect(self.__mis_root + '/labels.db')
        cmd = 'create table if not exists img (fname char(255),pred_label int, label int,title char(255),who char(128));'
        conn.execute(cmd)
        cmd = 'create index if not exists img_idx on img(fname);'
        conn.execute(cmd)
        conn.close()


    def get_user(self, who):
        ''' 用于存储 user 相关的 '''
        if who in self.__users:
            return self.__users[who]
        else:
            user = UserTask(who, self.__mis_root)
            self.__users[who] = user
            return user


    def next_image(self, user):
        ut = self.get_user(user)
        return ut.next_image()


    def save_cf_result(self, key, label, user):
        ''' 保存标定结果 '''
        ut = self.get_user(user)
        global cf
        title = cf.title(int(label))
        ut.save_image_result(key, label, title)


    def skip(self, key, user):
        ut = self.get_user(user)
        ut.skip(key)


    def cancel_last(self, user):
        ''' 撤销最后的保存 '''
        ut = self.get_user(user)
        ut.cancel()

    def redo(self, user, fname):
        self.get_user(user).redo(fname)


    def next_sid(self):
        self.__next_sid += 1
        return str(self.__next_sid)

    
    def get_session(self, sid):
        if sid in self.__sessions:
            return self.__sessions[sid]
        else:
            return None
        

    def cb(self, rc):
        #print rc
        pass


    def list_sessions(self):
        ss = []
        for s in self.__sessions:
            ss.append(self.__sessions[s].descr())
        return ss


    def create_session(self, url, interval, notify_url):
        global cb
        sid = self.next_sid()
        s = Session(cb, self, sid, url = url, interval = interval, notify_url = notify_url)
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

    
    def create_media2image(self, user, mid, fname):
        dst_path = self.__mis_root + '/' + mid
        try:
            os.mkdir(dst_path)
        except:
            pass

        mi = Media2Image(user, fname, (256, 256), 0.2, dst_path)
        self.__mis[mid] = mi

        return mi


    def get_media2image(self, mid):
        if mid in self.__mis:
            return self.__mis[mid]
        else:
            return None


    def destroy_media2image(self, mid):
        mi = self.get_media2image(mid)
        if mi is not None:
            mi.stop()
            del self.__mis[mid]


class NoCacheHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


class BaseRequest(tornado.web.RequestHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

    def get_current_user(self):
        return self.get_secure_cookie('user')


class LoginHandler(BaseRequest):
    def get(self):
        loc = self.get_query_argument('loc', '/')
        self.write('<html><body><form action="/login" method="post">'
                'Name: <input type="text" name="name">'
                '<input type="submit" value="Sign in">'
                '<input type="hidden" name="loc" value="' + loc + '">'
                '</form></body></html>')

    def post(self):
        self.set_secure_cookie('user', self.get_argument('name'))
        self.redirect(self.get_argument('loc'))


class RetrainIndexHandler(BaseRequest):
    def get(self):
        if not self.current_user:
            self.redirect("/login" + "?loc=" + self.request.uri)
            return
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.render('retrain_index.html')

    def post(self):
        ''' 总是来自 nginx 的 /after_upload，此时文件已经存储，
        '''
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        fname = self.get_argument('file_name')
        path = self.get_argument('store_path')
        print fname, path
        # FIXME: 因为 fname 可能包含非安全 url 字符，直接使用 path 的文件名部分吧
        fname = os.path.basename(path)
        mid = self.application.create_media2image(self.current_user, fname, path)
        self.render('media2image.html', fname = path, sname = fname)


class RetrainMedia2ImageHandler(BaseRequest):
    def get(self):
        if not self.current_user:
            self.redirect("login" + "?loc=" + self.request.uri)
            return

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        mid = self.get_query_argument('mid')
        mi = self.application.get_media2image(mid)
        frames = mi.frames()    # 已经转换的帧数 ..
        if mi.is_finished():
            self.application.destroy_media2image(mi)
            self.finish("finished " + str(frames))
        else:
            self.finish("running " + str(frames))


class RetrainShowingHandler(BaseRequest):
    def get(self):
        if not self.current_user:
            self.redirect("login" + "?loc=" + self.request.uri)
            return

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.render('showing.html')


class RetrainNextImageHandler(BaseRequest):
    def get(self):
        if not self.current_user:
            self.redirect("login" + "?loc=" + self.request.uri)
            return

        # 如果不设置，ie 将使用 cache ...
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

        fname = self.application.next_image(self.current_user)
        print 'next:', fname
        if fname is None:
            self.finish('None')
        else:
            # fname 为绝对路径，转换为 /imgs/mid/xxx 格式
            pos = fname.find('/imgs/')
            if pos == -1:
                self.finish('None')
            else:
                basefname = fname[pos:]

                # 预测结果，返回 { 'url': basefname, 'pred': xxxx }
                global cf, lock
                lock.acquire()
                img = caffe.io.load_image(fname) # 加载图片 ..
                pred = cf.predicate(img)
                lock.release()
                print 'pred:', pred[0][1], pred[0][2]
                self.application.get_user(self.current_user).save_image_pred_result(fname, pred[0][0])
                rx = { 'url': basefname,    #
                       'label': str(pred[0][0]),
                       'key': fname,        # 当确认是，需要更新数据库 ..
                       'pred': {
                            'top1': '{} {}'.format(pred[0][1], pred[0][2]),
                            'top2': '{} {}'.format(pred[1][1], pred[1][2]),
                            'top3': '{} {}'.format(pred[2][1], pred[2][2]),
                       },
                       'title': pred[0][1],
                }
                self.finish(rx)


class RetrainImageCfHandler(BaseRequest):
    def put(self):
        ''' body 为 json 格式，key 为文件名（对应数据库中的 fname），
            label 为对应的类别 ...
        '''
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        j = json.loads(self.request.body)
        key = j['key'].encode('utf-8')      # json 返回 unicode
        title = j['title'].encode('utf-8')  # 
        global cf
        label = cf.title2label(title)
        user = self.current_user

        print 'confirmed:', key, label, user, title

        self.application.save_cf_result(key, label, user)
        self.finish('OK')


class RetrainImageSkipHandler(BaseRequest):
    def put(self):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        j = json.loads(self.request.body)
        key = j['key'].encode('utf-8')      # json 返回 unicode
        print 'skip:', key, self.current_user

        self.application.skip(key, self.current_user)
        self.finish('OK')


class RetrainImageCancelHandler(BaseRequest):
    def put(self):
        ''' 撤销最后的选择 ...'''
        user = self.current_user
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

        print 'undo:', user
        self.application.cancel_last(user)
        self.finish('OK')


class RetrainImageRedoHandler(BaseRequest):
    def put(self):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        j = json.loads(self.request.body)
        key = j['key'].encode('utf-8')      # json 返回 unicode
        print 'redo:', key, self.current_user
        self.application.redo(self.current_user, key)
        self.finish('OK')


class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class GetClassifierLabelsHandler(tornado.web.RequestHandler):
    def get(self):
        global cf
        labels = cf.get_labels()
        labels.sort()

        # 整理为 json 格式
        self.finish({'labels': labels})

class CreateSessionHandler(tornado.web.RequestHandler):
    def post(self):
        j = json.loads(self.request.body)
        url = j['url']
        interval = j['interval']
        if 'notify_url' in j:
            notify_url = j['notify_url']
        else:
            notify_url = None
        sid = self.application.create_session(url = j['url'], interval = interval, notify_url = notify_url)
        rx = { "error": 0, "sessionid": sid, 'host_clock': time.time()}
        self.finish(rx)

    def get(self):
        # 列出当前的 session
        ss = self.application.list_sessions()
        rx = { 'num': len(ss), 'sessions': ss }
        self.finish(rx)


class DelSessionHandler(tornado.web.RequestHandler):
    def get(self, sid):
        # 返回 sid 对应的描述 ...
        s = self.application.get_session(sid)
        if s is None:
            self.clear()
            self.set_status(404)
            self.finish('<html><body> sessionid {} NOT found!</body></html>'.format(sid))
        else:
            self.finish(s.descr())


    def delete(self, sid):
        rx = { "error": 0, "sessionid": sid }
        rc = self.application.destory_session(sid)
        if not rc:
            self.clear()
            self.set_status(404)
            self.finish('<html><body> sessionid {} NOT found!</body></html>'.format(sid))
        else:
            self.finish(rx)


class SessionHandler(tornado.web.RequestHandler):
    def get(self, sid, cmd):
        if cmd == 'query':
            begin = float(self.get_query_argument('start', '0.0'))
            end = float(self.get_query_argument('stop', 'inf'))

            rcs = self.application.query_session(sid, begin, end)
            if rcs is None:
                self.clear()
                self.set_status(404)
                self.finish('<html><body> sessionid {} NOT found!</body></html>'.format(sid))
            else:
                rx = { 'state': '', 'results': rcs }
                if self.application.is_running(sid):
                    rx['state'] = 'running'
                else:
                    rx['state'] = 'stopped'
                self.finish(rx)
        else:
            self.clear()
            self.set_status(400)
            self.finish('<html><body> unknown command <b>{}</b> </body></html>'.format(cmd))


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
        global cf,lock

        body = self.request.body
        try:
            img = Image.open(StringIO.StringIO(body))
            img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
            lock.acquire()
            pred = cf.predicate(img)
            lock.release()
            rx = { "result": [] }
            for i in range(0, 3):
                r = { 'title': pred[i][1], 'score': float(pred[i][2]) }
                rx['result'].append(r)
            self.finish(rx)
        except Exception as e:
            print e
            self.finish(str(e))



# 仅仅用于单幅图片的分类，对于 url，还是启动独立的工作进程搞吧 ..
cf = Classifier('../models/deploy.prototxt',
    '../models/pretrained.caffemodel',
    '../models/mean.binaryproto',
    '../models/labels.txt', gpu=False)


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8899)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

