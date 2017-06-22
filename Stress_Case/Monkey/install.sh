#!/bin/bash
adb -s $1 wait-for-devices root
sleep 2
ls -l apk/| grep -v total |awk '{print $9}' |while read line;
do
   adb -s $1 install apk/$line
  echo $line done.
done
