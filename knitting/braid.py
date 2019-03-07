#!/usr/local/bin/python3

from sys import argv, stderr
from ribs import CabledKnitter

def usage():
    print('Usage: ' + argv[0] + ' input_file.csv')

# if len(argv) != 2:
    # usage()
    # exit()

left = list(range(0, 4))
mid = list(range(4, 8))
right = list(range(8, 12))

def knit_alt_rows(knitter, n):
    for i in range(n):
        for c in range(len(knitter.k.carriers)):
            knitter.new_row()
            knitter.knit(knitter.n_hooks, c)
            knitter.knit_row()

def knit_plain_cable_rows(knitter, carrier_order, n):
    for row in range(n):
        # print(list(reversed(left)), file=stderr)
        knitter.k.knits('+', 'f', left, [carrier_order[0]] * 4)
        knitter.k.knits('-', 'f', list(reversed(left)), [carrier_order[0]] * 4)
        knitter.k.knits('+', 'f', mid, [carrier_order[1]] * 4)
        knitter.k.knits('-', 'f', list(reversed(mid)), [carrier_order[1]] * 4)
        knitter.k.knits('+', 'f', right, [carrier_order[2]] * 4)
        knitter.k.knits('-', 'f', list(reversed(right)), [carrier_order[2]] * 4)

knitter = CabledKnitter(n_hooks=12, carriers=[7, 8, 9])
knitter.cast_on()
knit_alt_rows(knitter, 3)
carrier_order = [0, 1, 2]
row_height = 2
for i in range(4):
    knit_plain_cable_rows(knitter, carrier_order, row_height)
    knitter.k.miss('+', 'f', 13, carrier_order[0])
    knitter.k.miss('+', 'f', 13, carrier_order[1])
    knitter.swap_stitches(left, mid)
    knitter.just_do_swaps()
    carrier_order = [carrier_order[1], carrier_order[0], carrier_order[2]]

    knit_plain_cable_rows(knitter, carrier_order, row_height)
    knitter.swap_stitches(right, mid)
    knitter.just_do_swaps()
    carrier_order = [carrier_order[0], carrier_order[2], carrier_order[1]]

knit_plain_cable_rows(knitter, carrier_order, row_height)
knit_alt_rows(knitter, 5)
knitter.end()
