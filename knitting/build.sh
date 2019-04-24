#!/bin/bash

clear
clear
clear


case "$1" in
    "23")
        ./two_thirds.py > knitout-files/two_thirds.k
        ../../knitout-backend-swg/knitout-to-dat.js knitout-files/two_thirds.k dat-files/two_thirds.dat
        ;;
    "braid")
        ./braid.py "${@:2}" > knitout-files/braid.k
        ../../knitout-backend-swg/knitout-to-dat.js knitout-files/braid.k dat-files/fancier-braid.dat
        ;;
    "lace")
        ./lace.py "${@:2}" > knitout-files/lace.k
        ../../knitout-backend-swg/knitout-to-dat.js knitout-files/lace.k dat-files/lace.dat
        ;;
    "tube")
        ./tube.py "${@:2}" > knitout-files/tube.k
        ../../knitout-backend-swg/knitout-to-dat.js knitout-files/tube.k dat-files/tube.dat
        ;;
    "meta")
        ./metaknit.py > knitout-files/circle.k
        ../../knitout-backend-swg/knitout-to-dat.js knitout-files/circle.k dat-files/circle.dat
        ;;
    "illusion")
        ./illusion.py  "${@:2}" > knitout-files/illusion.k
        ../../knitout-backend-swg/knitout-to-dat.js knitout-files/illusion.k dat-files/illusion.dat
        ;;
    "fi")
        ./single_bed_img.py "${@:2}" > knitout-files/faire_isle.k
        ../../knitout-backend-swg/knitout-to-dat.js knitout-files/faire_isle.k dat-files/faire_isle.dat
        ;;
esac


