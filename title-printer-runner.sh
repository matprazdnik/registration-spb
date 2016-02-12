#!/bin/bash

exec >> title-printer.log 2>&1
while : ; do
  ./title-printer.py
  sleep 1
done
