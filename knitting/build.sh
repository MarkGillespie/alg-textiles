#!/bin/bash

clear
clear
clear

#./tube.py $1.csv > $1.k
#../../knitout-backend-swg/knitout-to-dat.js $1.k $1.dat

./braid.py > knitout-files/braid.k
../../knitout-backend-swg/knitout-to-dat.js knitout-files/braid.k dat-files/braid.dat
