#!/usr/local/bin/python3

from sys import stdout, stderr, argv
from lace_knitter import LaceKnitter

def usage():
    print('Usage: ' + argv[0] + ' input.lace')

if len(argv) != 2:
    usage()
    exit()

reps = 4
pattern = []

with open(argv[1]) as f:
    w = int(f.readline()[2:-1])
    for row in f:
        row_stitches = 0

        row = row[:-1] # remove newline at end of row
        for c in row:
            if c not in [' ', '\\', '/', 'o']:
                raise Exception('Character \'' + c + '\' not recognized. Stitches must be \' \'(space), \'o\', \'\\\', or \'/\'')
        if len(row) < w:
            row += ' ' * (w - len(row))
        pattern.append(row)
pattern = list(reversed(pattern))

lace = LaceKnitter(n_stitches=w)
lace.cast_on()

for i in range(10):
    lace.new_row()
    lace.knit(n=w)
    lace.knit_row()


for rep in range(reps):
    for row in pattern:
        lace.new_row()
        for c in row:
            if c == ' ':
                lace.knit()
            elif c == 'o':
                lace.increase_knit()
            elif c == '/':
                lace.decrease_knit(front='l')
            elif c == '\\':
                lace.decrease_knit(front='r')
            elif c == 'M':
                lace.decrease_two_knit(front='c')
            elif c == 'λ':
                lace.decrease_two_knit(front='r')
        lace.knit_row()

        lace.new_row()
        lace.knit(n=w)
        lace.knit_row()


for i in range(10):
    lace.new_row()
    lace.knit(n=w)
    lace.knit_row()
lace.end()
