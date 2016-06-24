import dbhlp
import random
import subprocess
import sys
import sqlite3 as sq
import threading

def get_database_record(fname):
    conn = sq.connect(fname)
    cmd = 'select fname , label from img where label >= 0'
    cursor = self.__conn.execute(cmd)
    return  cursor.fetchall()

def change_solver(val):
    with open('solver0.prototxt', 'r') as fp:
        kvs = fp.readlines()
    k, v = kvs[1].split(":")
    kvs[1] = k + ' ' + str(val) + ' \n'

    with open('solver.prototxt', 'w') as fp:
        fp.writelines(kvs)

def get_txt(datas, fname):
    s = ''
    for e in datas:
        s = s + e[0].encode('utf-8') + ' ' + str(e[1]) + '\n'
    with open(fname, 'w') as fp:
        fp.write(s)



if __name__ == '__main__':
    imagelist = get_database_records('labels.db')
    random.shuffle(imagelist)
    
    length = len(imagelist) * 4 / 5
    train = []
    val = []
    for i in range(len(imagelist)):
       if i <= length:
           train.append(imagelist[i])
       else:
           val.append(imagelist[i])
       
    get_txt(train, 'train.txt')
    get_txt(val, 'val.txt')

    change_solver(len(val)) 

    commands = ['caffe.bin', 'train', '-solver', \
               'solver.prototxt', \
               '-weights', 'caffenet.caffemodel', '-gpu', 'all'] 
    # we must return information of train
    subprocess.call(commands)
