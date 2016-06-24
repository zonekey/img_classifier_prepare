#!/usr/bin/python
# coding: utf-8
#
# @file: usertask.py
# @date: 2016-06-17
# @brief:
# @detail:
#
#################################################################

from dbhlp import DB


''' 对应一个 user 的操作，
        1. 维护分类的 undo 栈
        2. ...
'''

class UserTask:
    def __init__(self, user, rootpath, db):
        self.__user = user
        self.__db = db
        self.__undo = []
        self.__prop = {}
        self.__imgs_root = rootpath  # FIXME: 存储转换后的图片 ..., 图片保存在 imgs_root/mid 目录下
                                            # 不区分用户，这样可以多人同时分一个视频 ...


    def who(self):
        return self.__user


    def set_prop(self, key, value):
        self.__prop[key] = value


    def get(self, key, default = None):
        if key in self.__prop:
            return self.__prop[key]
        else:
            return default

    
    def next_image(self):
        ''' 返回用户相关的，对应 mid 目录下的下一张为分类的图片名字 '''
        return self.__db.next_fname(self.__user)


    def save_image_pred_result(self, fname, label):
        ''' 保存预测结果 '''
        self.__db.update_pred_result(fname, label)


    def save_image_result(self, fname, label, title):
        ''' 将 fname 对应的 label 保存到数据库中 '''
        print 'saving:', fname, self.__user, label, title
        self.__db.update_result(fname, label, title)
        self.__undo.append(fname)  # 准备撤销 ...


    def skip(self, fname):
        print 'skip:', fname, self.__user
        self.__db.skip(fname)
        self.__undo.append(fname)  # 允许撤销 ...

    def cancel(self):
        ''' 将 fname 对应的 label 置为 -1 '''
        if len(self.__undo) == 0:
            return

        fname = self.__undo.pop()
        print 'undo:', fname, self.__user
        self.__db.update_result(fname, -1, '.')



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

