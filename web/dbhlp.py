#!/usr/bin/python
# coding: utf-8
#
# @file: dbhlp.py
# @date: 2016-06-22
# @brief:
# @detail:
#
#################################################################


import sqlite3 as sq
import threading


''' 封装数据库操作，所有操作都序列化 ... '''
class DB:
    def __init__(self, fname):
        ''' fname: 为sqlite3的文件绝对路径 '''
        self.__conn = sq.connect(fname)
        self.__lock = threading.Lock()
        self.prepare_db()


    def __del__(self):
        self.__conn.close()


    def get_labeled(self):
        ''' 返回已经手动标定的条目数 '''
        cmd = 'select count(*) from img where label != -1;'
        cur = self.__conn.execute(cmd)
        c = cur.fetchone()
        return c[0]


    def get_total(self):
        ''' 返回所有记录 '''
        cmd = 'select count(*) from img;'
        cur = self.__conn.execute(cmd)
        c = cur.fetchone()
        return c[0]


    def prepare_db(self):
        ''' 在 self.__mis_root 下创建 labels.db，格式为：
                fname: 完整的文件路径名
                pred_label: int
                label: int
                title: label 的说明
                who: 登录者
        '''
        cmd = 'create table if not exists img (fname char(255),pred_label int, label int,title char(255),who char(128));'
        self.__conn.execute(cmd)
        cmd = 'create index if not exists img_idx on img(fname);'
        self.__conn.execute(cmd)
        self.__conn.commit()



    def next_fname(self, who):
        ''' 优先返回 who 对应的 label = -1 的 fname，否则返回其他 who 的 label = -1 的记录，否则 None
        '''
        cmd = 'select fname from img where who=="{}" and label=-1 order by fname;'.format(who)
        cursor = self.__conn.execute(cmd)
        r = cursor.fetchone()
        if r is not None:
            return r[0]

        cmd = 'select fname from img where label=-1 order by fname;'
        cursor = self.__conn.execute(cmd)
        r = cursor.fetchone()
        if r is None:
            return None

        # 更新 who
        cmd = 'update img set who="{}" where fname="{}";'.format(who, r[0])
        self.__conn.execute(cmd)
        self.__conn.commit()
        return r[0]


    def update_pred_result(self, fname, pred_label):
        ''' 更新 pred_label 字段 '''
        cmd = 'update img set pred_label={} where fname="{}";'.format(pred_label, fname)
        self.__conn.execute(cmd)
        self.__conn.commit()


    def update_result(self, fname, label, title):
        ''' 更新 label, title 字段 '''
        cmd = 'update img set label={},title="{}" where fname="{}";'.format(label, title, fname)
        self.__conn.execute(cmd)
        self.__conn.commit()


    def skip(self, fname):
        ''' 设置 label 为 -2 标识为“跳过” ...'''
        cmd = 'update img set label=-2 where fname="{}";'.format(fname)
        self.__conn.execute(cmd)
        self.__conn.commit()


    def labeled_all(self):
        ''' 返回 fname, label '''
        cmd = 'select fname,label from img where label>=0;'
        cursor = self.__conn.execute(cmd)
        return cursor.fetchall()




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

