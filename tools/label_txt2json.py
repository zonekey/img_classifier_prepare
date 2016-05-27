#!/usr/bin/python
# coding: utf-8
#
# @file: p.py
# @date: 2016-05-27
# @brief:
# @detail:
#
#################################################################

import json

j = { "root": "./", "catalogs": [] }

label = 0
f = open('labels.txt', 'r')
for line in f:
    line = line.strip()
    item = { 'label': label, 'titles': [line] }
    j["catalogs"].append(item)
    label += 1

f.close()

s = str(json.dumps(j, ensure_ascii=False))

f = open('catalogs.json', 'w')
f.write(s)
f.close()




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

