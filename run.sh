#!/bin/bash

name=mf
cd /var/www/$name/$name
kill $(<$name.pid)
nohup python3 $name.py >> $name.log 2>&1 &
echo $! > $name.pid
sleep 1
tail $name.log
