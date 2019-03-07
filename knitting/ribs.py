from knitout import Knitout
from sys import stdout, stderr

class RibbedKnitter:
    def __init__(self, n_hooks=10, out_file=stdout, carriers=[6], gauge=15, spacing=1):
        self.k = Knitout(out_file=out_file, carriers=carriers, gauge=gauge)
        self.n_hooks = n_hooks;
        self.spacing = spacing

    def cast_on(self):
        self.k.cast_on('f', 0, self.spacing * (self.n_hooks-1), self.spacing)

        # True = knit, False = purl
        self.stitches        = [True for _ in range(self.n_hooks)]
        self.stitch_beds     = ['f'  for _ in range(self.n_hooks)]

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

        self.k.cast_off(direction, 'f', carrier, 0, self.n_hooks, self.spacing)

    def end(self):
        for i in range(len(self.k.carriers)):
            self.k.outhook(i)

    def new_row(self):
        self.stitches = []
        self.stitch_carriers = []

    def perform_transfers(self):
        if len(self.stitches) != self.n_hooks:
            raise Exception('Row length ' + str(len(self.stitches)) + ' not equal to number of hooks ' + str(self.n_hooks))
        for i in range(self.n_hooks):
            if self.stitches[i] and self.stitch_beds[i] == 'b':
                self.k.from_xfer('b', 'f', i * self.spacing)
                self.stitch_beds[i] = 'f'
            elif not self.stitches[i] and self.stitch_beds[i] == 'f':
                self.k.from_xfer('f', 'b', i * self.spacing)
                self.stitch_beds[i] = 'b'

    def move_all_to_front(self):
        for i in range(self.n_hooks):
            if self.stitch_beds[i] == 'b':
                self.k.from_xfer('b', 'f', i * self.spacing)
                self.stitch_beds[i] = 'f'

    def move_carrier_stitches_to_correct_bed(self, carrier):
        for i in range(self.n_hooks):
            if self.stitch_carriers[i] == carrier and not self.stitches[i]:
                self.k.from_xfer('f', 'b', i * self.spacing)
                self.stitch_beds[i] = 'b'


    def knit_row(self):
        if len(self.stitches) != self.n_hooks:
            raise Exception('Row length ' + str(len(self.stitches)) + ' not equal to number of hooks ' + str(self.n_hooks) + '\n ' + str(self.stitches))

        if all(carrier == self.stitch_carriers[0] for carrier in self.stitch_carriers):
            carrier = self.stitch_carriers[0]
            self.knit_monochromatic_row(carrier)
        else:
            self.knit_polychromatic_row()


    def knit_polychromatic_row(self):
        carriers = list(set(self.stitch_carriers)) # dedupe
        self.move_all_to_front()

        for carrier in carriers:
            self.move_carrier_stitches_to_correct_bed(carrier)
            if self.direction_is_positive:
                for i in range(self.n_hooks):
                    if self.stitch_carriers[i] == carrier:
                        self.k.knit('+', self.stitch_beds[i], i * self.spacing, carrier)
                self.k.miss('+', 'f', self.n_hooks * self.spacing, carrier)
            else:
                for i in range(self.n_hooks-1, -1, -1):
                    if self.stitch_carriers[i] == carrier:
                        self.k.knit('-', self.stitch_beds[i], i * self.spacing, carrier)
                self.k.miss('-', 'f', -1, carrier)
        self.direction_is_positive = not self.direction_is_positive

    def knit_monochromatic_row(self, carrier):
        self.perform_transfers()
        if self.direction_is_positive:
            for i in range(self.n_hooks):
                self.k.knit('+', self.stitch_beds[i], i * self.spacing, carrier)
        else:
            for i in range(self.n_hooks-1, -1, -1):
                self.k.knit('-', self.stitch_beds[i], i * self.spacing, carrier)
        self.direction_is_positive = not self.direction_is_positive

    def knit(self, n=1, carrier=0):
        self.stitches += n * [True]
        self.stitch_carriers += n * [carrier]

    def purl(self, n=1, carrier=0):
        self.stitches += n * [False]
        self.stitch_carriers += n * [carrier]

class CabledKnitter(RibbedKnitter):
    def __init__(self, n_hooks=10, out_file=stdout, carriers=[6], gauge=15):
        # spacing must be 1 so cables don't stretch too far
        super().__init__(n_hooks=n_hooks, out_file=out_file, carriers=carriers, gauge=gauge, spacing=1)
        self.swaps = []
        self.spacing = 1

    def new_row(self):
        super().new_row()
        self.swaps = []

    def validate_swap(self, front_indices, back_indices):
        """Interchange the stitches in positions front_indices with the stitches
           in positions back_indices. Assumes that front_indices and back_indices
           are each contiguous, and that the two sets of stitches are adjacent."""
        front_indices.sort()
        back_indices.sort()

        if front_indices != list(range(front_indices[0], front_indices[-1]+1)):
            raise Exception('front_indices not contiguous: ' + str(front_indices))
        if back_indices != list(range(back_indices[0], back_indices[-1]+1)):
            raise Exception('back_indices not contiguous: ' + str(back_indices))

        if (front_indices[0] < back_indices[0] and front_indices[-1] > back_indices[0]) \
            or (front_indices[0] > back_indices[0] and front_indices[0] < back_indices[-1]):
                raise Exception('perform_swap encountered overlapping index sets: ' \
                        + str(front_indices) + ' and ' + str(back_indices))

        if front_indices[-1] + 1 != back_indices[0] and front_indices[0] != back_indices[-1] + 1:
            raise Exception('index sets not adjacent: front_indices: ' + str(front_indices) \
                    + ', back_indices: ' + str(back_indices))
        return (front_indices, back_indices)

    def swap_stitches(self, front_indices, back_indices):
        (front_indices, back_indices) = self.validate_swap(front_indices, back_indices)
        if front_indices[0] < back_indices[0]:
            front_rack =  self.spacing * len(back_indices)
            back_rack  = -self.spacing * len(front_indices)
        else:
            front_rack = -self.spacing * len(back_indices)
            back_rack  =  self.spacing * len(front_indices)
        self.swaps.append((front_indices, front_rack, back_indices, back_rack));

    def perform_swaps(self):
        # transfer all stitches that need to be swapped to the back bed
        # This selects the ones currently in the front bed and moves them back
        swapped_indices = []
        transfer_indices = []
        for (front_indices, _, back_indices, _) in self.swaps:
            swapped_indices += front_indices
            swapped_indices += back_indices

        # transfer all stitches to back
        transfer_indices = list({i for i in swapped_indices if self.stitch_beds[i] == 'f'})
        self.k.from_xfers('f', 'b', transfer_indices)
        for i in transfer_indices:
            self.stitch_beds[i] = 'b';

        done_front = [False for i in range(len(self.swaps))]
        done_back  = [False for i in range(len(self.swaps))]

        # set comprehension to dedupe list
        rack_positions = list({y for (_, front_rack, _, back_rack) in self.swaps for y in [front_rack, back_rack]})

        # sort to do smaller stretches first
        rack_positions = sorted(rack_positions, key=abs)

        # set up a dictionary to associate a set of swaps to each rack position
        swaps_from_rack = dict((pos, []) for pos in rack_positions)
        for i in range(len(self.swaps)):
                (front_indices, front_rack, back_indices, back_rack) = self.swaps[i]
                swaps_from_rack[front_rack].append(i)
                swaps_from_rack[back_rack].append(i)

        for rack_position in rack_positions:
            self.k.rack(rack_position)
            for i in swaps_from_rack[rack_position]:
                (front_indices, front_rack, back_indices, back_rack) = self.swaps[i]
                if front_rack == rack_position:
                    self.k.from_xfers('b', 'f', [i * self.spacing for i in front_indices])
                    done_front[i] = True
                elif done_front[i]:
                    self.k.from_xfers('b', 'f', [i * self.spacing for i in back_indices])
                    done_back[i] = True
        for rack_position in rack_positions:
            self.k.rack(rack_position)
            for i in swaps_from_rack[rack_position]:
                (front_indices, front_rack, back_indices, back_rack) = self.swaps[i]
                if back_rack == rack_position and not done_back[i]:
                    self.k.from_xfers('b', 'f', [i * self.spacing for i in back_indices])
                    done_back[i] = True

        self.k.rack(0)
        for i in swapped_indices:
            self.stitch_beds[i] = 'f'


    def knit_row(self):
        super().knit_row()
        self.perform_swaps()
        self.swaps = []

    def just_do_swaps(self):
        self.perform_swaps();
        self.swaps = []
