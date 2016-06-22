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

    
    def next_image(self):
        ''' 返回用户相关的，对应 mid 目录下的下一张为分类的图片名字 '''
        if self.__pending_img_fname is None:
            self.__pending_img_fname = self.next_uncf_image()
        return self.__pending_img_fname


    def save_image_pred_result(self, fname, label):
        ''' 保存预测结果 '''
        conn = sq.connect(self.db_name())
        cmd = 'update img set pred_label={} where fname="{}";'.format(label, fname)
        conn.execute(cmd)
        conn.commit()
        conn.close()


    def save_image_result(self, fname, label, title):
        ''' 将 fname 对应的 label 保存到数据库中 '''
        if fname == self.__pending_img_fname:
            self.__pending_img_fname = None

        self.__undo.append(fname)
        conn = sq.connect(self.db_name())
        cmd = 'update img set label={},title="{}" where fname = "{}";'.format(label, title, fname)
        conn.execute(cmd)
        conn.commit()
        conn.close()


    def cancel(self):
        ''' 将 fname 对应的 label 置为 -1 '''
        if len(self.__undo) == 0:
            return
        fname = self.__undo.pop()
        self.__pending_img_fname = None
        conn = sq.connect(self.db_name())
        cmd = 'update img set label=-1,title="." where fname = "{}";'.format(fname)
        conn.execute(cmd)
        conn.commit()
        conn.close()


    def db_name(self):
        '''
            数据库在分解图片时，已经创建，格式为 fname(char), label(int), title(char), who(char)
        '''
        return self.__imgs_root + '/labels.db'


    def next_uncf_image(self):
        ''' 优先返回 who = user 的 label = -1 的记录，如果自己上传的都标定完成了，则
            返回其他人的 label = -1 的记录 ...，并改为自己的名字 ..

            多个人同时标定时，有问题：
                一个人预选了一张图片，但另一个标完自己图片的人，有可能会选择相同的文件。
            但这样似乎问题也不大，总是记录最后一个人的标定结果和名字 ...
        '''

        conn = sq.connect(self.db_name())
        cmd = 'select fname from img where label = -2 and who = "{}" order by fname desc;'.format(self.__user)
        cursor = conn.execute(cmd)
        fs = cursor.fetchone()
        if fs is None:
            cmd = 'select fname from img where label = -1 order by fname desc;'
            cursor = conn.execute(cmd)
            fs = cursor.fetchone()
            if fs is None:
                conn.close()
                return None
        
        fname = fs[0]
        cmd = 'update img set who = "{}" where fname = "{}";'.format(self.__user, fname)
        conn.execute(cmd)
        conn.commit()
        conn.close() 
        return fname




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

