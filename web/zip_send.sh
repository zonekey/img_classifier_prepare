#!/bin/sh
#rm -f ../models/pretrained.caffemodel
mv ../models/pretrained.caffemodel training/tmp-_iter_1000.caffemodel
cp  training/tmp-_iter_1000.caffemodel ../models/pretrained.caffemodel
zip -o pub/m.zip ../models/deploy.prototxt  ../models/labels.txt  ../models/mean.binaryproto  ../models/pretrained.caffemodel   
curl -X PUT -d '{"url": "http://172.16.1.60:8890/pub/m.zip}' "http://${2}:18000/train/api/update?func=start_download"
