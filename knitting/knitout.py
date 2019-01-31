from sys import stdout

class Knitout:
    def __init__(self, out_file=stdout, hooks=list(range(10)), carriers=[6], gauge=15):
        self.carriers = carriers
        self.hooks = hooks
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
        print('tuck ' + direction + ' ' + bed + str(self.hooks[hook]) + ' ' + str(self.carriers[carrier]), file=self.out_file)

    def miss(self, direction, bed, hook, carrier):
        print('miss ' + direction + ' ' + bed + str(self.hooks[hook]) + ' ' + str(self.carriers[carrier]), file=self.out_file)

    def xfer(self, from_bed, from_hook, to_bed, to_hook):
        print('xfer ' + from_bed + str(self.hooks[from_hook]) + ' ' + to_bed + str(self.hooks[to_hook]), file=self.out_file)

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
        print('knit ' + direction + ' ' + bed + str(self.hooks[hook]) + ' ' + str(self.carriers[carrier]), file=self.out_file)

    def knits(self, direction, bed, hooks, carriers):
        for (hook, carrier) in zip(hooks, carriers):
            self.knit(direction, bed, hook, carrier)

    def rack(self, n):
        self.rack_pos = n;
        print('rack ' + str(n), file=self.out_file)

    def cast_on(self, bed, carrier):
        self.inhook(carrier)
        for i in range(len(self.hooks)-1, 0, -2):
            self.tuck('-', bed, i, carrier)

        if len(self.hooks) % 2 == 0:
            start = 0
            self.miss('-', bed, 0, carrier)
        else:
            start = 1

        for i in range(start, len(self.hooks), 2):
            self.knit('+', bed, i, carrier)

        self.miss('+', bed, len(self.hooks)-1, carrier)

        self.releasehook(carrier)

    def cast_off(self, direction, bed, carrier):
        if (bed == 'f'):
            opp = 'b'
        elif (bed == 'b'):
            opp = 'f'
        else:
            raise Exception('invalid bed: ' + bed)

        if (direction == '+'):
            for i in range(0, len(self.hooks)-1):
                self.from_xfer(bed, opp, i)
                self.rack(1)
                self.from_xfer(opp, bed, i)
                self.rack(0)
                self.knit('+', bed, i+1, carrier)
                if i % 15 == 0:
                    self.tuck('-', opp, i, carrier)
        elif (direction == '-'):
            for i in range(len(self.hooks)-1, 0, -1):
                self.from_xfer(bed, opp, i)
                self.rack(-1)
                self.from_xfer(opp, bed, i)
                self.rack(0)
                self.knit('-', bed, i-1, carrier)
                if i % 15 == 0:
                    self.tuck('+', opp, i, carrier)
        else:
            raise Exception('invalid direction: ' + direction)

        self.outhook(carrier)
