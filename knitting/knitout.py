from sys import stdout
from math import copysign

class Knitout:
    def __init__(self, out_file=stdout, carriers=[6], gauge=15):
        self.carriers = carriers
        self.rack_pos = 0
        file=self.out_file = out_file
        print(';!knitout-2', file=self.out_file)
        print(';;Machine: SWGXYZ', file=self.out_file)
        print(';;Carriers: 1 2 3 4 5 6 7 8 9 10', file=self.out_file)
        print(';;Gauge: ' + str(gauge), file=self.out_file)

    def x_stitch_number(self, n):
        print('x-stitch-number ' + str(n), file=self.out_file)

    def inhook(self, carrier):
        print('inhook ' + str(self.carriers[carrier]), file=self.out_file)

    def outhook(self, carrier):
        print('outhook ' + str(self.carriers[carrier]), file=self.out_file)

    def releasehook(self, carrier):
        print('releasehook ' + str(self.carriers[carrier]), file=self.out_file)

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

    # xfer with hook given relative to from_bed
    def to_xfer(self, from_bed, to_bed, hook):
        self.xfer(from_bed, hook - self.rack_pos, to_bed, hook)

    def knit(self, direction, bed, hook, carrier):
        print('knit ' + direction + ' ' + bed + str(hook) + ' ' + str(self.carriers[carrier]), file=self.out_file)

    def knits(self, direction, bed, hooks, carriers):
        for (hook, carrier) in zip(hooks, carriers):
            self.knit(direction, bed, hook, carrier)

    def rack(self, n):
        self.rack_pos = n;
        print('rack ' + str(n), file=self.out_file)

    def cast_on(self, bed, start, end, spacing=1):
        self.inhook(0)
        for i in range(end, start-1, -2 * spacing):
            self.tuck('-', bed, i, 0)

        if (end - start + 1) % 2 == 0:
            row_start = start
            self.miss('-', bed, start, 0)
        else:
            row_start = start + spacing 

        for i in range(row_start, end, 2 * spacing):
            self.knit('+', bed, i, 0)

        self.miss('+', bed, end + 1, 0)
        self.releasehook(0)

        for carrier in range(1, len(self.carriers)):
            self.inhook(carrier)
            for i in range(end, start-1, -spacing):
                self.knit('-', bed, i, carrier)
            for i in range(start, end+1, spacing):
                self.knit('+', bed, i, carrier)
            self.releasehook(carrier)

    # TODO: fix spacing at ends
    def cast_on_tube(self, start, end, spacing=1):
        self.inhook(0)

        back_offset = spacing-1
        for i in range(end, start-1, -2 * spacing):
            self.tuck('-', 'f', i, 0)

        if (end - start + 1) % 2 == 0:
            row_start = start
            back_row_start = start + spacing
            self.miss('-', 'f', start, 0)
        else:
            row_start = start + spacing 
            back_row_start = start

        for i in range(row_start, end, 2 * spacing):
            self.tuck('+', 'b', i + back_offset, 0)

        for i in range(end - spacing, start-1, -2 * spacing):
            self.knit('-', 'f', i, 0)

        for i in range(back_row_start, end, 2 * spacing):
            self.knit('+', 'b', i + back_offset, 0)

        for i in range(end, start-1, -spacing):
            self.knit('-', 'f', i, 0)

        for i in range(start, end+1, spacing):
            self.knit('+', 'b', i + back_offset, 0)

        self.releasehook(0)

    # start = lower index, end = higher index
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

        self.outhook(carrier)
