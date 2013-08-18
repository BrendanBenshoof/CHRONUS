#!/bin/bash

for i in {12002..12100}; 
do 
    python chord.py $i 127.0.0.1 12001 & 
done
