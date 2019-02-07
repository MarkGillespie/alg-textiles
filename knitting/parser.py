import csv
from ribs import CabledKnitter
from enum import Enum
from sys import stderr

csv.register_dialect('cables', delimiter = ' ')

purl = '.'
knit = '|'
left = '/'
right = '\\'
under = '-'
symbols = [purl, knit, left, right, under]

class Stitch(Enum):
    knit = 1
    purl = 2
    knit_left = 3
    knit_right = 4
    swap_left_over = 5
    swap_right_over = 6

def count_run_length(stitch_list, i):
    current_char = stitch_list[i]
    j = i + 1
    while j < len(stitch_list) and stitch_list[j] == current_char:
        j += 1
    return j, j - i

def next_stitch_group(stitch_list, position):
    current_char = stitch_list[position]
    if current_char not in symbols:
        raise Exception('Did not recognize symbol ' + current_char)

    start_index = position 
    if current_char in [purl, knit, left]:
        position, width = count_run_length(stitch_list, position)

        if current_char == knit:
            stitch = Stitch.knit
        elif current_char == purl:
            stitch = Stitch.purl
        elif current_char == left:
            stitch = Stitch.knit_left

    elif current_char == right:
        position, n_over = count_run_length(stitch_list, position)

        if position >= len(stitch_list):
            raise Exception('Tried to move right off edge')
        if stitch_list[position] == under:
            position, n_under = count_run_length(stitch_list, position)
            stitch = Stitch.swap_left_over
            width = (n_over, n_under)
        else:
            stitch = Stitch.knit_right
            width = n_over
    elif current_char == under:
        position, n_under = count_run_length(stitch_list, position)

        if position >= len(stitch_list):
            raise Exception('Ended on unmatched ' + under)

        next_char = stitch_list[position]
        if next_char not in [left, right]:
            raise Exception('Symbol ' + under + ' not next to cable transfer')

        moving_left = (next_char == left);

        position, n_over = count_run_length(stitch_list, position)

        if position < len(stitch_list):
            if stitch_list[position] == under:
                position, more_under = count_run_length(stitch_list, position)
                n_under += more_under
        
        stitch = None
        if moving_left == True:
            stitch = Stitch.swap_right_over
            width = (n_under, n_over)
        else:
            stitch = Stitch.swap_left_over
            width = (n_over, n_under)

    instruction = (stitch, width, start_index)
    return instruction, position 

def parse_row(stitch_list):
    stitch_groups = []
    position = 0
    while position < len(stitch_list):
        instruction, position = next_stitch_group(stitch_list, position)
        stitch_groups.append(instruction)

    return stitch_groups

def knit_row(knitter, row):
    knitter.new_row()
    stitches = parse_row(row)
    for (stitch, width, start_index) in stitches:
        if stitch == Stitch.knit:
            knitter.knit(width, 0)
        elif stitch == Stitch.purl:
            knitter.purl(width, 1)
        elif stitch == Stitch.knit_left:
            knitter.knit(width, 0)
            knit_indices = list(range(start_index, start_index + width))
            knitter.swap_stitches(knit_indices, [start_index - 1])
        elif stitch == Stitch.knit_right:
            knitter.knit(width, 0)
            knit_indices = list(range(start_index, start_index + width))
            knitter.swap_stitches(knit_indices, [start_index + width])
        elif stitch == Stitch.swap_left_over:
            (left_width, right_width) = width
            knitter.knit(left_width + right_width, 0)
            left_indices = list(range(start_index, start_index + left_width))
            right_indices = list(range(start_index + left_width, start_index + left_width + right_width))
            knitter.swap_stitches(left_indices, right_indices)
        elif stitch == Stitch.swap_right_over:
            (left_width, right_width) = width
            knitter.knit(left_width + right_width, 0)
            left_indices = list(range(start_index, start_index + left_width))
            right_indices = list(range(start_index + left_width, start_index + left_width + right_width))
            knitter.swap_stitches(right_indices, left_indices)
        else:
            raise Exception('Stitch ' + stitch + ' not recognized')
    knitter.knit_row()

def parse_cable_file(file_name):
    with open(file_name) as file:
        reader  = csv.reader(file, dialect='cables')
        knitter = None

        for row in reader:
            if knitter is None:
                knitter = CabledKnitter(n_hooks=len(row), carriers=[3, 6])
                knitter.cast_on()
            knit_row(knitter, row)
        knitter.end()
        # knitter.cast_off()
