#!/usr/bin/python
# coding: utf-8
#
# @file: picstore.py
# @date: 2016-06-16
# @brief:
# @detail:
#
#################################################################


''' 存储图片 '''

import os


def is_image(fname):
    img_exts = ['.jpg', '.jpeg', '.png' ]
    (root, ext) = os.path.splitext(fname)
    if ext in img_exts:
        return True


class PicStore:
    def __init__(self, orin_path, labeled_path):
        self.__orin_path = orin_path
        self.__labeled_path = labeled_path


    def next(self):
        ''' 返回 origin path 中下一个文件，如无，则返回 None，如有，将文件移动到
            labeled_path 中，同时返回 labeled_path 中的完整文件名字 '''
        l = os.listdir(self.__orin_path)
        if len(l) == 0:
            return None

        src_fname = None
        for fn in l:
            fn = os.path.abspath(fn)
            if os.path.isfile(fn) and is_image(fn):
                src_fname = fn
                break

        if src_fname is None:
            return None

        basefn = os.path.basefilename(src_fname)
        dst_fname = os.path.abspath(self.__labeled_path) + '/' + basefn

        os.rename(img_fname, dst_fname)
        return dst_fname






# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

