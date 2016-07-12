import dbhlp
import random
import subprocess, time
import sys, os, signal
from dbhlp import DB
import threading

def get_database_record(fname):
    db = DB(fname)
    return db.labeled_all()


def change_solver(val):
    with open('solver0.prototxt', 'r') as fp:
        kvs = fp.readlines()
    k, v = kvs[1].split(":")
    kvs[1] = k + ': ' + str(val) + ' \n'

    with open('solver.prototxt', 'w') as fp:
        fp.writelines(kvs)


def change_solver2(cfg):
    with open('cfg/solver0.prototxt', 'r') as f:
        lines = f.readlines()

        w = open('training/solver.prototxt', 'w')

        for line in lines:
            line = line.strip()
            k, v = line.split(':')
            if k in cfg:
                w.write(k + ':' + cfg[k] + '\n')
            else:
                w.write(k + ':' + v + '\n')
        w.close()
                


def get_txt(datas, fname):
    s = ''
    for e in datas:
        s = s + e[0].encode('utf-8') + ' ' + str(e[1]) + '\n'
    with open(fname, 'w') as fp:
        fp.write(s)



caffe = None
quit = False

def signal_handler(signal, f):
    if caffe:
        caffe.terminate()
    quit = True
    sys.exit()


if __name__ == '__main__':
    os.environ['ONLINE_TRAIN'] = 'true'
    imagelist = get_database_record(sys.argv[1])
    random.shuffle(imagelist)

    length = len(imagelist) * 4 / 5
    train = []
    val = []
    for i in range(len(imagelist)):
       if i <= length:
           train.append(imagelist[i])
       else:
           val.append(imagelist[i])
    os.environ["TRAIN_NUM"] = str(len(train))
    os.environ["TEST_NUM"] = str(len(val))
    os.environ['GLOG_minloglevel'] = '5'

       
    get_txt(train, 'train.txt')
    get_txt(val, 'val.txt')


    cfg = { 
        'test_iter': str(len(val)),
    }

#    change_solver2(cfg)

    print "FT: 0 0 0 0 0"
    sys.stdout.flush()

    signal.signal(signal.SIGTERM, signal_handler)

    commands = ['caffe.bin', 'train', '-solver', \
               'training/solver.prototxt', \
               '-weights', '../models/pretrained.caffemodel', '-gpu', 'all'] 

    caffe = subprocess.Popen(commands)

    while not quit:
        time.sleep(1.0)
        

