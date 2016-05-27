#!/bin/bash

if [ -f 'deploy.prototxt' ];
then
	echo 'deploy.prototxt exist'
else
	ln -s /usr/local/share/shanghai/deploy.prototxt  deploy.prototxt
fi

if [ -f 'pretrained.caffemodel' ];
then
	echo 'pretrained.caffemodel exist'
else
	ln -s /usr/local/share/shanghai/last.caffemodel pretrained.caffemodel
fi

if [ -f 'mean.binaryproto' ];
then
	echo 'mean.binaryproto exist'
else
	ln -s /usr/local/share/shanghai/mean.binaryproto mean.binaryproto
fi

if [ -f 'labels.txt' ];
then
	echo 'labels.txt exist'
else
	ln -s /usr/local/share/shanghai/labels.txt labels.txt
fi

