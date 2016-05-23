#!/usr/bin/env sh
# Compute the mean image from the imagenet training lmdb
# N.B. this is available in data/ilsvrc12


compute_image_mean.bin train_lmdb  mean.binaryproto

echo "Done."
