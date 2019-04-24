#!/usr/local/bin/python3

from sys import argv, stderr
from math import copysign
from knitout import Knitout

def usage():
    print('Usage: ' + argv[0] + ' input.braid')

if len(argv) != 2:
    usage()
    exit()

reps = 3
row_height = 6
n = None
swaps = []
with open(argv[1]) as f:
    n = int(f.readline()[2:-1])
    for row in f:
        swaps.append([int(i) for i in (row[:-1]).split()])

strip_width = 4
k = Knitout(use_presser=True)
k.cast_on_single_carrier('f', 0, n * strip_width - 1)
for i in range(3):
    k.knits('-', 'f', range(n*strip_width-1, -1, -1), 0)
    k.knits('+', 'f', range(0, n*strip_width), 0)

strip_hooks = []
for i in range(n):
    hooks = list(range(i * strip_width, (i+1) * strip_width))
    reversed_hooks = hooks[::-1]
    strip_hooks.append([h + 4 * i for h in hooks])

    k.inhook(0)
    k.knits('-', 'f', reversed_hooks, 0)
    k.knits('+', 'f', hooks, 0)
    k.releasehook(0)
    for j in range(reps * row_height * len(swaps)):
        k.knits('-', 'f', reversed_hooks, 0)
        k.knits('+', 'f', hooks, 0)
    k.outhook(0)

for i in range(1, n):
    hooks = list(range(i * strip_width + (i-1)*strip_width, n*strip_width + (i-1)*strip_width))
    k.from_xfers('f', 'b', hooks)
    k.rack(strip_width)
    k.from_xfers('b', 'f', hooks)
    k.rack(0)

# does a bunch of swaps assuming they all have the same sign
def do_swaps(k, swaps, strip_hooks):
    if not swaps:
        return

    front_hooks = []
    back_hooks  = []
    for s in swaps:
        front_strip = abs(s)-1
        if swaps[0] > 0:
            back_strip = front_strip+1
        else:
            back_strip = front_strip-1

        front_hooks += strip_hooks[front_strip]
        back_hooks  += strip_hooks[back_strip]

    offset = int(copysign(strip_width, swaps[0]))
    k.from_xfers('f', 'b', front_hooks + back_hooks)
    k.rack(offset)
    k.from_xfers('b', 'f', front_hooks)
    k.rack(0)
    k.from_xfers('f', 'b', [i + offset for i in front_hooks])
    k.rack(2 * offset)
    k.drop('f', -5)
    k.rack(offset)
    k.from_xfers('b', 'f', [i + offset for i in front_hooks])


    offset = int(copysign(strip_width, -swaps[0]))
    k.rack(offset)
    k.from_xfers('b', 'f', back_hooks)
    k.rack(0)
    k.from_xfers('f', 'b', [i + offset for i in back_hooks])
    k.rack(2 * offset)
    k.drop('f', -5)
    k.rack(offset)
    k.from_xfers('b', 'f', [i + offset for i in back_hooks])
    k.rack(0)

for i in range(reps):
    for swap_row in swaps:
        # swaps to the right
        pos_swaps = [s for s in swap_row if s > 0]
        do_swaps(k, pos_swaps, strip_hooks)
        # swaps to the left
        neg_swaps = [s for s in swap_row if s < 0]
        print(neg_swaps, file=stderr)
        do_swaps(k, neg_swaps, strip_hooks)

for i in range(n-1, 0, -1):
    hooks = list(range(i * strip_width + i*strip_width, n*strip_width + i*strip_width))
    k.from_xfers('f', 'b', hooks)
    k.rack(-strip_width)
    k.from_xfers('b', 'f', hooks)
    k.rack(0)

k.inhook(0)
k.knits('-', 'f', range(n*strip_width-1, -1, -1), 0)
k.knits('+', 'f', range(0, n*strip_width), 0)
k.releasehook(0)
for i in range(4):
    k.knits('-', 'f', range(n*strip_width-1, -1, -1), 0)
    k.knits('+', 'f', range(0, n*strip_width), 0)
k.outhook(0)
