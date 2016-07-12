#!/bin/sh
mkdir -p packet

if [ $1 = '0' ]; then
    cp ../models/pretrained.caffemodel packet/pretrained.caffemodel
else
    cp  training/tmp-_iter_${1}.caffemodel packet/pretrained.caffemodel
fi

zip -o pub/m.zip ../models/deploy.prototxt  ../models/labels.txt  ../models/mean.binaryproto  packet/pretrained.caffemodel   

ip=$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')
echo $ip
curl -X PUT -d '{"url": "http://${ip}:8889/pub/m.zip}' "http://${2}:18000/train/api/update?func=start_download"
