#!/usr/local/bin/python3

from sys import argv
from graph import Graph

def usage():
    print('Usage: ' + argv[0] + ' input_file.obj')

if len(argv) != 2:
    usage()
    exit()

with open(argv[1], 'r') as f:
    graph = Graph(f)
f.closed

points = graph.traversal_point_list()

CRLF = '\r\n'

line_number = 1
for p in points:
    scaled_x = 0.1 + p.x * 9.8
    scaled_y = 0.1 + p.y * 9.8
    pt = "X{:.3f}Y{:.3f}".format(
            round(scaled_x * 1000.0) / 1000.0,
            round(scaled_y * 1000.0) / 1000.0
    )
    if line_number == 1:
        print("N" + str(line_number) + "G00" + pt, end=CRLF)
    else:
        print("N" + str(line_number) + "G01" + pt, end=CRLF)
    line_number += 1
print("N" + str(line_number) + "M02", end=CRLF)
