#!/bin/bash

for fname in *.jpg
do
	mv $fname 'c-'$fname
done
