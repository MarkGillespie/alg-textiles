from sys import stdout, stderr
from knitout import Knitout

class LaceKnitter():
    def __init__(self, n_stitches=10, out_file=stdout, carriers=[6], gauge=15):
        self.n = n_stitches
        self.out_file = out_file
        self.carriers = carriers
        self.gauge = gauge

        self.stitch_hooks        = []
        self.behind              = []
        self.current_hook        = 0
        self.current_stitch      = 0
        self.stitch_carriers     = []
        self.k = Knitout(carriers=carriers, gauge=gauge, out_file=out_file)

    def new_row(self):
        self.stitch_carriers     = []
        self.stitches            = []
        self.stitch_hooks        = []
        self.current_hook        = 0
        self.current_stitch      = 0
        self.behind              = self.n * [False]

    def knit_row(self):
        self.perform_transfers()

        if self.direction_is_positive:
            for i in range(self.n):
                self.k.knit('+', self.stitch_beds[i], i, self.stitch_carriers[i])
        else:
            for i in range(self.n-1, -1, -1):
                self.k.knit('-', self.stitch_beds[i], i, self.stitch_carriers[i])
        self.direction_is_positive = not self.direction_is_positive

    def get_offset_to_stitch_map(self, offsets, stitches=None):
        if not stitches:
            stitches = list(range(len(offsets)))

        offset_amts = sorted(list(set(offsets)))
        offset_stitches = {}
        for off in offset_amts:
            these_stitches = []
            for i in range(len(offsets)):
                if offsets[i] == off:
                    these_stitches.append(stitches[i])
            offset_stitches[off] = these_stitches
        return (offset_amts, offset_stitches)

    def compute_offsets(self):
        return [self.stitch_hooks[i] - i for i in range(len(self.stitch_hooks))]

    # increases and decreases
    def perform_transfers(self):
        front_stitch_present = [False] * self.n
        back_stitch_waiting_list = [None] * self.n

        offsets = self.compute_offsets()
        (offset_amts, offset_stitches) = self.get_offset_to_stitch_map(offsets)

        if sum([abs(o) for o in offsets]) > 0:
            front_bed_stitches = [i for i in range(self.n) if self.stitch_beds[i] == 'f']
            back_bed_stitches  = [i for i in range(self.n) if self.stitches[i] == False]
            self.k.from_xfers('f', 'b', front_bed_stitches)

            for off in offset_amts:
                self.k.rack(off)
                back_stitches_to_fix = []
                for stitch in offset_stitches[off]:
                    if (not self.behind[stitch]) or front_stitch_present[stitch + off]:
                        self.k.from_xfer('b', 'f', stitch)
                        front_stitch_present[stitch + off] = True
                        if back_stitch_waiting_list[stitch + off]:
                            back_stitches_to_fix.append(back_stitch_waiting_list[stitch + off])
                    else:
                        back_stitch_waiting_list[stitch + off] = (stitch, off)

                back_offsets  = [off for (stitch, off) in back_stitches_to_fix]
                back_stitches = [stitch for (stitch, off) in back_stitches_to_fix]
                (back_offset_amts, back_offset_stitches) = self.get_offset_to_stitch_map(back_offsets, back_stitches)

                for back_off in back_offset_amts:
                    self.k.rack(back_off)
                    self.k.from_xfers('b', 'f', back_offset_stitches[back_off])

            self.k.rack(0)
            self.k.from_xfers('f', 'b', back_bed_stitches)
            self.stitch_beds = ['f'] * self.n
            for i in range(self.n):
                if self.stitches[i] == False:
                    self.stitch_beds[i] = 'b'
        else:
            front_to_back_stitches = [i for i in range(self.n) if self.stitch_beds[i] == 'f' and self.stitches[i] == False]
            back_to_front_stitches = [i for i in range(self.n) if self.stitch_beds[i] == 'b' and self.stitches[i] == True]
            if len(front_to_back_stitches) > 0:
                self.k.from_xfers('f', 'b', front_to_back_stitches)
            if len(back_to_front_stitches) > 0:
                self.k.from_xfers('b', 'f', back_to_front_stitches)
            self.stitch_beds = ['f'] * self.n
            for i in range(self.n):
                if self.stitches[i] == False:
                    self.stitch_beds[i] = 'b'

    def increase_knit(self, carrier=0):
        self.stitches        += [True]
        self.stitch_carriers += [carrier]
        self.current_hook    += 1

    # front must be 'l' or 'r'
    def decrease_knit(self, front='l', carrier=0):
        self.stitches            += [True]
        self.stitch_carriers     += [carrier]
        self.stitch_hooks        += 2 * [self.current_hook]
        self.current_hook        += 1

        if (front == 'l'):
            self.behind[self.current_stitch + 1] = True
        elif (front == 'r'):
            self.behind[self.current_stitch + 0] = True

        self.current_stitch    += 2

    # front must be 'l', 'c', or 'r'
    def decrease_two_knit(self, front='c', carrier=0):
        self.stitches            += [True]
        self.stitch_carriers     += [carrier]
        self.stitch_hooks        += 3 * [self.current_hook]
        self.current_hook        += 1

        if (front == 'l'):
            self.behind[self.current_stitch + 1] = True
            self.behind[self.current_stitch + 2] = True
        elif (front == 'c'):
            self.behind[self.current_stitch + 0] = True
            self.behind[self.current_stitch + 2] = True
        elif (front == 'r'):
            self.behind[self.current_stitch + 0] = True
            self.behind[self.current_stitch + 1] = True

        self.current_stitch    += 3

    def knit(self, n=1, carrier=0):
        self.stitches            += n * [True]
        self.stitch_carriers     += n * [carrier]
        self.stitch_hooks        += list(range(self.current_hook, self.current_hook + n))
        self.current_hook        += n
        self.current_stitch      += n

    def purl(self, n=1, carrier=0):
        self.stitches            += n * [False]
        self.stitch_carriers     += n * [carrier]
        self.stitch_hooks        += list(range(self.current_hook, self.current_hook + n))
        self.current_hook        += n
        self.current_stitch      += n

    def cast_on(self):
        self.k.cast_on('f', 0, self.n-1, 1)

        # True = knit, False = purl
        self.stitches    = [True] * self.n
        self.stitch_beds = ['f']  * self.n

        # True = +, False = -
        self.direction_is_positive = False
        self.k.x_stitch_number(78)

    def cast_off(self, carrier=0):
        for other_carrier in self.k.carriers:
            if other_carrier != carrier:
                self.k.outhook(self.k.carriers.index(other_carrier))

        if self.direction_is_positive:
            direction = '+'
        else:
            direction = '-'

        self.k.cast_off(direction, 'f', carrier, 0, self.n, self.spacing)

    def end(self):
        for i in range(len(self.k.carriers)):
            self.k.outhook(i)
