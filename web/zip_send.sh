#!/bin/sh
cp  training/tmp-_iter_${1}.caffemodel ../models/pretrained.caffemodel
ip= ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'

zip -o pub/m.zip ../models/deploy.prototxt  ../models/labels.txt  ../models/mean.binaryproto  ../models/pretrained.caffemodel   
curl -X PUT -d '{"url": "http://${ip}:8889/pub/m.zip}' "http://${2}:18000/train/api/update?func=start_download"
