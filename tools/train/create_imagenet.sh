#!/usr/bin/env sh
# Create the imagenet lmdb inputs
# N.B. set the path to the imagenet train + val data dirs

# Set RESIZE=true to resize the images to 256x256. Leave as false if images have
# already been resized using another tool.
RESIZE=true
if $RESIZE; then
  RESIZE_HEIGHT=28
  RESIZE_WIDTH=28
else
  RESIZE_HEIGHT=0
  RESIZE_WIDTH=0
fi

echo "Creating train lmdb..."

GLOG_logtostderr=1 convert_imageset.bin \
    --resize_height=$RESIZE_HEIGHT \
    --resize_width=$RESIZE_WIDTH \
    --shuffle \
	--gray=true \
    ../images/ \
    ../images/train.txt \
    train_lmdb

echo "Creating val lmdb..."

GLOG_logtostderr=1 convert_imageset.bin \
    --resize_height=$RESIZE_HEIGHT \
    --resize_width=$RESIZE_WIDTH \
    --shuffle \
	--gray=true \
    ../images/ \
    ../images/val.txt \
    val_lmdb

echo "Done."
