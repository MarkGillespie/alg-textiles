#!/usr/local/bin/python3

from sys import stdout, stderr, argv
from lace_knitter import LaceKnitter
import argparse

def read_pattern(filename):
    with open(filename) as f:
        pattern = []
        w = int(f.readline()[2:-1])
        for row in f:
            row_stitches = 0

            row = row[:-1] # remove newline at end of row
            for c in row:
                if c not in [' ', '\\', '/', 'o', '.', 'M', 'λ']:
                    raise Exception('Character \'' + c + '\' not recognized. Stitches must be \' \'(space), \'o\', \'\\\', or \'/\'')
            if len(row) < w:
                row += ' ' * (w - len(row))
            pattern.append(row)
        return list(reversed(pattern))

parser = argparse.ArgumentParser(description='Converts *.lace files into knitout.')
parser.add_argument('patterns', nargs='+')
args = vars(parser.parse_args())

width  = 45
height = 25
border_width = 5
total_width = width + 2 * border_width
patterns = []
for pattern in args['patterns']:
    patterns.append(read_pattern(pattern))

lace = LaceKnitter(n_stitches=total_width)
lace.cast_on()

for i in range(10):
    lace.new_row()
    lace.knit(n=total_width)
    lace.knit_row()

for i in range(len(patterns)):
    pattern = patterns[i]
    pattern_height = len(pattern)
    pattern_width  = len(pattern[0])
    reps           = int(width / pattern_width)
    if reps == 0:
        raise Exception('Error: pattern ' + args['patterns'][i] + ' cannot fit in ' + str(width) + ' stitches')
    left_extra_border  = int((width - reps * pattern_width) / 2)
    right_extra_border = width - reps * pattern_width - left_extra_border

    for y in range(height):
        lace.new_row()
        lace.knit(n=(border_width + left_extra_border))
        for rep in range(reps):
            for c in pattern[y%pattern_height]:
                if c == ' ':
                    lace.knit()
                elif c == '.':
                    lace.purl()
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
        lace.knit(n=(border_width + right_extra_border))
        lace.knit_row()

        lace.new_row()
        lace.knit(n=(border_width + left_extra_border))
        for rep in range(reps):
            for c in pattern[y%pattern_height]:
                if c == '.':
                    lace.purl()
                else:
                    lace.knit()
        lace.knit(n=(border_width + right_extra_border))
        lace.knit_row()

    for i in range(10):
        lace.new_row()
        lace.knit(n=total_width)
        lace.knit_row()
lace.end()
