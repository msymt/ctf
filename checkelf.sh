#!/bin/bash

if [ -n "$1" ]
then
  file "$1"
  checksec --file "$1"
  ldd "$1" > ldd.txt
  objdump -d -M intel "$1" > objdump.txt
  readelf -a "$1" > readelf.txt
  rp --file "$1" --unique --rop 5 > rp.txt 
else
  echo "usage [checkelf][ELF program]"
fi
