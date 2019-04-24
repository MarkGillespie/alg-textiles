from sys import stdout, stderr
from math import copysign, floor
import warnings

class Knitout:
    def __init__(self, out_file=stdout, carriers=[6], gauge=15, use_presser=False):
        self.carriers = carriers
        self.rack_pos = 0
        self.use_presser = use_presser
        self.inhooked_carriers = []
        self.yarn_holding_hook_out = False
        file=self.out_file = out_file
        print(';!knitout-2', file=self.out_file)
        print(';;Machine: SWGXYZ', file=self.out_file)
        print(';;Carriers: 1 2 3 4 5 6 7 8 9 10', file=self.out_file)
        print(';;Gauge: ' + str(gauge), file=self.out_file)

    def x_stitch_number(self, n):
        print('x-stitch-number ' + str(n), file=self.out_file)

    # The 'x-presser-mode' command sets the fabric presser mode to 'off' (no fabric presser), 'auto' (fabric presser on passes with only front or only back stitches), or 'on' (break passes so that fabric presser can always be used). The default mode is 'off'.
    def x_presser_mode(self, mode):
        print('x-presser-mode ' + mode, file=self.out_file)

    def inhook(self, carrier):
        if carrier in self.inhooked_carriers:
            warnings.warn('carrier ' + str(carrier) + ' already inhooked.', UserWarning)
            return

        if self.use_presser:
            self.x_presser_mode('off')
        print('inhook ' + str(self.carriers[carrier]), file=self.out_file)
        self.inhooked_carriers.append(carrier)
        self.yarn_holding_hook_out = True

    def outhook(self, carrier):
        if carrier not in self.inhooked_carriers:
            raise Exception('carrier ' + str(carrier) + ' cannot be outhooked before it is inhooked.')

        if self.use_presser:
            self.x_presser_mode('off')
        print('outhook ' + str(self.carriers[carrier]), file=self.out_file)
        self.inhooked_carriers.remove(carrier)

    def releasehook(self, carrier):
        if carrier not in self.inhooked_carriers:
            raise Exception('carrier ' + str(carrier) + ' cannot be released before it is inhooked.')
        if not self.yarn_holding_hook_out:
            warnings.warn('triend to releasehook when yarn holding hook is not out.')
            return

        print('releasehook ' + str(self.carriers[carrier]), file=self.out_file)
        if self.use_presser:
            self.x_presser_mode('auto')
        self.yarn_holding_hook_out = False

    def tuck(self, direction, bed, hook, carrier):
        print('tuck ' + direction + ' ' + bed + str(hook) + ' ' + str(self.carriers[carrier]), file=self.out_file)

    def miss(self, direction, bed, hook, carrier):
        print('miss ' + direction + ' ' + bed + str(hook) + ' ' + str(self.carriers[carrier]), file=self.out_file)

    def xfer(self, from_bed, from_hook, to_bed, to_hook):
        print('xfer ' + from_bed + str(from_hook) + ' ' + to_bed + str(to_hook), file=self.out_file)

    # xfer with hook given relative to from_bed
    def from_xfer(self, from_bed, to_bed, hook):
        self.xfer(from_bed, hook, to_bed, hook + self.rack_pos)

    def from_xfers(self, from_bed, to_bed, hooks):
        hooks.sort()
        for hook in hooks:
            self.from_xfer(from_bed, to_bed, hook)

    # xfer with hook given relative to to_bed
    def to_xfer(self, from_bed, to_bed, hook):
        self.xfer(from_bed, hook - self.rack_pos, to_bed, hook)

    def to_xfers(self, from_bed, to_bed, hooks):
        hooks.sort()
        for hook in hooks:
            self.to_xfer(from_bed, to_bed, hook)

    def drop(self, bed, hook):
        print('drop ' + bed + str(hook), file=self.out_file)

    def knit(self, direction, bed, hook, carrier):
        print('knit ' + direction + ' ' + bed + str(hook) + ' ' + str(self.carriers[carrier]), file=self.out_file)

    def knits(self, direction, bed, hooks, carrier):
        for hook in hooks:
            self.knit(direction, bed, hook, carrier)

    def multicarrier_knits(self, direction, bed, hooks, carriers):
        for (hook, carrier) in zip(hooks, carriers):
            self.knit(direction, bed, hook, carrier)

    def rack(self, n):
        self.rack_pos = n;
        print('rack ' + str(n), file=self.out_file)

    def cast_on_single_carrier(self, bed, start, end, spacing=1, carrier=0):
        self.inhook(carrier)
        for i in range(end, start-1, -2 * spacing):
            self.tuck('-', bed, i, carrier)

        if (end - start + 1) % 2 == 0:
            row_start = start
            self.miss('-', bed, start, carrier)
        else:
            row_start = start + spacing

        for i in range(row_start, end, 2 * spacing):
            self.knit('+', bed, i, carrier)

        self.miss('+', bed, end + 1, carrier)
        self.releasehook(carrier)

    def cast_on(self, bed, start, end, spacing=1):
        self.cast_on_single_carrier(bed, start, end, spacing, 0)
        for carrier in range(1, len(self.carriers)):
            self.inhook(carrier)
            for i in range(end, start-1, -spacing):
                self.knit('-', bed, i, carrier)
            for i in range(start, end+1, spacing):
                self.knit('+', bed, i, carrier)
            self.releasehook(carrier)

    def cast_on_closed_tube_single_carrier(self, start, end, spacing=1, carrier=0):
        self.inhook(carrier)
        for i in range(end, start-1, -spacing):
            if (i / spacing) % 2 == (end/spacing)%2:
                self.tuck('-', 'f', i, carrier)
            else:
                self.tuck('-', 'b', i, carrier)

        for i in range(start, end+1, spacing):
            if (i / spacing) % 2 == (end/spacing)%2:
                self.tuck('+', 'b', i, carrier)
            else:
                self.tuck('+', 'f', i, carrier)

        self.miss('+', 'f', end + 1, carrier)
        self.releasehook(carrier)

    # TODO: fix spacing at ends
    def cast_on_tube(self, start, end, spacing=1):
        self.inhook(0)

        side_len = floor((end + 1 - start) / spacing)
        print(side_len, file=stderr)
        back_offset = spacing-1
        if side_len % 2 == end % 2:
            back_row_start = start + 1
            self.miss('-', 'f', start, 0)
        else:
            back_row_start = start

        for i in range(end, start-1, -2 * spacing):
            self.tuck('-', 'f', i, 0)

        for i in range(back_row_start, end+1, 2 * spacing):
            self.tuck('+', 'b', i + back_offset, 0)

        self.releasehook(0)

        for i in range(end - spacing, start-1, -2 * spacing):
            self.tuck('-', 'f', i, 0)

        for i in range(back_row_start+spacing, end, 2 * spacing):
            self.tuck('+', 'b', i + back_offset, 0)

        for i in range(end, start-1, -spacing):
            self.knit('-', 'f', i, 0)

        for i in range(back_row_start, end+1, spacing):
            self.knit('+', 'b', i + back_offset, 0)

    # start = lower index, end = higher index
    # Warning: doesn't outhook - you have to do that yourself
    def cast_off(self, direction, bed, carrier, start, end, spacing=1):
        if (bed == 'f'):
            opp = 'b'
        elif (bed == 'b'):
            opp = 'f'
        else:
            raise Exception('invalid bed: ' + bed)

        if (direction == '+'):
            for i in range(start, end, spacing):
                self.from_xfer(bed, opp, i)
                self.rack(spacing)
                self.from_xfer(opp, bed, i)
                self.rack(0)
                self.knit('+', bed, i+spacing, carrier)
                if i % 15 == 0:
                    self.tuck('-', opp, i, carrier)
        elif (direction == '-'):
            for i in range(end, start, -spacing):
                self.from_xfer(bed, opp, i)
                self.rack(-spacing)
                self.from_xfer(opp, bed, i)
                self.rack(0)
                self.knit('-', bed, i-spacing, carrier)
                if i % 15 == 0:
                    self.tuck('+', opp, i, carrier)
        else:
            raise Exception('invalid direction: ' + direction)
