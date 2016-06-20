#!/usr/bin/python
# coding: utf-8
#
# @file: usertask.py
# @date: 2016-06-17
# @brief:
# @detail:
#
#################################################################

import sqlite3 as sq


''' 对应一个 user 的操作，
        1. 维护分类的 undo 栈
        2. ...
'''

class UserTask:
    def __init__(self, user, rootpath):
        self.__user = user
        self.__undo = []
        self.__prop = {}
        self.__imgs_root = rootpath  # FIXME: 存储转换后的图片 ..., 图片保存在 imgs_root/mid 目录下
                                            # 不区分用户，这样可以多人同时分一个视频 ...
        self.__pending_img_fname = None     # 调用 next_image() 之后，save_image_result() 之前，保存文件名字


    def who(self):
        return self.__user


    def set_prop(self, key, value):
        self.__prop[key] = value


    def get(self, key, default = None):
        if key in self.__prop:
            return self.__prop[key]
        else:
            return default

    
    def next_image(self, mid):
        ''' 返回用户相关的，对应 mid 目录下的下一张为分类的图片名字 '''
        if self.__pending_img_fname is None:
            # 从 img_path 中找到一张没有标定过的图片
            self.__pending_img_fname = self.next_uncf_image(mid)
        return self.__pending_img_fname


    def save_image_result(self, mid, fname, label):
        ''' 将 fname 对应的 label 保存到数据库中 '''
        if fname == self.__pending_img_fname:
            self.__pending_img_fname = None

        self.__undo.append(fname)
        conn = sq.connect(self.db_name(mid))
        cmd = 'update img set label = {} where fname = "{}"'.format(label, fname)
        conn.execute(cmd)
        conn.commit()
        conn.close()


    def cancel(self, mid):
        ''' 将 fname 对应的 label 置为 -1 '''
        if len(self.__undo) == 0:
            return
        fname = self.__undo.pop()
        self.__pending_img_fname = None
        conn = sq.connect(self.db_name(mid))
        cmd = 'update img set label = -1,who="." where fname = "{}"'.format(fname)
        conn.execute(cmd)
        conn.commit()
        conn.close()


    def db_name(self, mid):
        ''' 每个 mid 对应一个数据库 
            数据库在分解图片时，已经创建，格式为 fname(char), label(int), who(char)
        '''
        return self.__imgs_root + '/' + mid + '/label.db'


    def img_path(self, mid):
        return self.__imgs_root + '/' + mid + '/'


    def next_uncf_image(self, mid):
        ''' 返回数据库中，label = -1，并且“无主” 的记录，选择后，update who '''
        conn = sq.connect(self.db_name(mid))
        cmd = 'select fname from img where label = -1 and who = "."'
        cursor = conn.execute(cmd)
        fs = cursor.fetchone()
        if fs is None:
            conn.close()
            return None
        
        fname = fs[0]
        cmd = 'update img set who = "{}" where fname = "{}"'.format(self.__user, fname)
        conn.execute(cmd)
        conn.commit()
        conn.close() 
        return fname




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

