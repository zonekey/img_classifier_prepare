#!/usr/bin/python
# coding: utf-8
#
# @file: baserequest.py
# @date: 2016-06-24
# @brief:
# @detail:
#
#################################################################

import tornado.web


class BaseRequest(tornado.web.RequestHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

    def get_current_user(self):
        return self.get_secure_cookie('user')





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

