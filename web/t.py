#!/usr/bin/python
# coding: utf-8
#
# @file: t.py
# @date: 2016-06-13
# @brief:
# @detail:
#
#################################################################

import time, sys

stamp = 1.0
for i in range(0, 100):
    print stamp, 'XXX', 0.90, 'YYY', 0.05, 'ZZZ', 0.03
    sys.stdout.flush()

    time.sleep(1)
    stamp += 1.01





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

