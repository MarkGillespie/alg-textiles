from sys import stdout, stderr
from knitout import Knitout

class LaceKnitter():
    def __init__(self, n_stitches=10, out_file=stdout, carriers=[6], gauge=15):
        self.n = n_stitches
        self.out_file = out_file
        self.carriers = carriers
        self.gauge = gauge

        self.stitches_consumed   = 0
        self.stitch_carriers     = []
        self.width_modifications = []
        self.k = Knitout(carriers=carriers, gauge=gauge, out_file=out_file)

    def new_row(self):
        self.stitches_consumed   = 0
        self.stitch_carriers     = []
        self.stitches            = []
        self.width_modifications = []

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
        self.width_modifications += [(0, self.stitches_consumed, None)]
        offsets = [0] * self.n
        behind  = [False] * self.n

        net_offset = 0
        for i in range(len(self.width_modifications) - 1):
            (amt, pos, front) = self.width_modifications[i]
            (_,   end, _)     = self.width_modifications[i+1]
            net_offset += amt

            for j in range(pos, min(end + 1, self.n)):
                offsets[j] = net_offset

            if amt == -1:
                if net_offset - amt > 0:
                    offsets[pos] = net_offset
                    if front == 'l':
                        behind[pos]   = True
                    elif front == 'r':
                        behind[pos-1] = True
                    else:
                        raise Exception('front variable \'' + str(front) + '\' should be \'l\' or \'r\'')
                else:
                    offsets[pos]  = net_offset - amt
                    if front == 'l':
                        behind[pos+1] = True
                    elif front == 'r':
                        behind[pos]   = True
                    else:
                        raise Exception('front variable \'' + str(front) + '\' should be \'l\' or \'r\'')
            elif amt == -2:
                if net_offset - amt > 0:
                    offsets[pos] = net_offset+1
                    if front == 'l':
                        behind[pos]   = True
                        behind[pos+1] = True
                    elif front == 'c':
                        behind[pos-1] = True
                        behind[pos+1] = True
                    elif front == 'r':
                        behind[pos-1] = True
                        behind[pos]   = True
                    else:
                        raise Exception('front variable \'' + str(front) + '\' should be \'l\' or \'r\'')
                else:
                    offsets[pos]    = net_offset - amt
                    offsets[pos+1]  = net_offset - amt - 1
                    if front == 'l':
                        behind[pos+1]  = True
                    elif front == 'c':
                        behind[pos]   = True
                    elif front == 'r':
                        behind[pos]   = True
                    else:
                        raise Exception('front variable \'' + str(front) + '\' should be \'l\' or \'r\'')
            elif amt == 1:
                if net_offset - amt >= 0:
                    pass
                else:
                    if net_offset - amt == -2:
                        offsets[pos] = 7#net_offset - amt
                    else:
                        offsets[pos] = net_offset - amt
            else:
                raise Exception('Invalid width: ' + str(amt))
        return (offsets, behind)

    # increases and decreases
    def perform_transfers(self):
        if len(self.width_modifications) <= 1:
            return
        front_stitch_present = [False] * self.n
        back_stitch_waiting_list = [None] * self.n

        (offsets, behind) = self.compute_offsets()
        (offset_amts, offset_stitches) = self.get_offset_to_stitch_map(offsets)

        # print(self.width_modifications, file=stderr)
        # print(offsets, file=stderr)
        # print(offset_stitches[0], file=stderr)
        # print("", file=stderr)

        if len(offset_amts) > 1 or offset_amts[0] != 0:
            front_bed_stitches = [i for i in range(self.n) if self.stitch_beds[i] == 'f']
            back_bed_stitches  = [i for i in range(self.n) if self.stitch_beds[i] == 'b']
            self.k.from_xfers('f', 'b', front_bed_stitches)

            for off in offset_amts:
                self.k.rack(off)
                back_stitches_to_fix = []
                for stitch in offset_stitches[off]:
                    if (not behind[stitch]) or front_stitch_present[stitch + off]:
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

    def increase_knit(self, carrier=0):
        self.width_modifications += [(+1, self.stitches_consumed, None)]

        self.stitches          += [True]
        self.stitch_carriers   += [carrier]
        self.stitches_consumed += 1

    # front must be 'l' or 'r'
    def decrease_knit(self, front='l', carrier=0):
        self.width_modifications += [(-1, self.stitches_consumed, front)]

        self.stitches          += [True]
        self.stitch_carriers   += [carrier]
        self.stitches_consumed += 1

    # front must be 'l', 'c', or 'r'
    def decrease_two_knit(self, front='c', carrier=0):
        self.width_modifications += [(-2, self.stitches_consumed, front)]

        self.stitches          += [True]
        self.stitch_carriers   += [carrier]
        self.stitches_consumed += 1

    def knit(self, n=1, carrier=0):
        self.stitches          += n * [True]
        self.stitch_carriers   += n * [carrier]
        self.stitches_consumed += 1

    def purl(self, n=1, carrier=0):
        self.stitches          += n * [False]
        self.stitch_carriers   += n * [carrier]
        self.stitches_consumed += 1

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
