#!/bin/bash

clear
clear
clear

./cables.py $1.csv > $1.k
../../knitout-backend-swg/knitout-to-dat.js $1.k $1.dat
