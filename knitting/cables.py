#!/usr/local/bin/python3

from sys import argv
from parser import parse_cable_file

def usage():
    print('Usage: ' + argv[0] + ' input_file.csv')

if len(argv) != 2:
    usage()
    exit()

parse_cable_file(argv[1])


