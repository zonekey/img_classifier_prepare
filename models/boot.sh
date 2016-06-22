rm pretrained.caffemodel mean.binaryproto deploy.prototxt labels.txt

MODEL_ROOT=/home/liuguangyuan0532/git/shanghai/data/image2.13.1/

MEAN=classrooms_mean.binaryproto
PRETRAIN=snapshot/caffenet_train_iter_17000.caffemodel
LABELS=labels.txt
DEPLOY=deploy.prototxt


ln -s $MODEL_ROOT/$PRETRAIN pretrained.caffemodel
ln -s $MODEL_ROOT/$MEAN mean.binaryproto
ln -s $MODEL_ROOT/$DEPLOY deploy.prototxt
ln -s $MODEL_ROOT/$LABELS labels.txt

