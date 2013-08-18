#!/bin/bash

for i in {12001..12200}; 
do 
    python chord.py $i 127.0.0.1 12000 & 
done
