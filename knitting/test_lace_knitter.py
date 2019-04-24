#!/usr/local/bin/python3

import unittest
import sys, os
from lace_knitter import LaceKnitter

def knit_pattern(knitter, pattern):
    knitter.new_row()
    for c in pattern:
        if c == '.':
            knitter.knit()
        elif c == 'o':
            knitter.increase_knit()
        elif c == '/':
            knitter.decrease_knit(front='l') 
        elif c == '\\':
            knitter.decrease_knit(front='r') 
        elif c == 'M':
            knitter.decrease_two_knit(front='c')
        elif c == 'λ':
            lace.decrease_two_knit(front='r')

class TestLace(unittest.TestCase):
    def setUp(self):
        self.null = open(os.devnull, 'w')
        self.knitter = LaceKnitter(10, out_file=self.null)

    def test_yarn_over_then_decrease_right(self):
        pattern = '..o/......'
        offset_answer  = [0, 0, 1, 0, 0] + 5 * [0]
        behind_answer  = [False, False, False, True, False] + 5 * [False]

        knit_pattern(self.knitter, pattern)
        (offsets, behind) = self.knitter.compute_offsets()

        self.assertEqual(offsets, offset_answer)
        self.assertEqual(behind,  behind_answer)

    def test_yarn_over_then_decrease_left(self):
        pattern = '..o\......'
        offset_answer  = [0, 0, 1, 0, 0] + 5 * [0]
        behind_answer  = [False, False, True, False, False] + 5 * [False]

        knit_pattern(self.knitter, pattern)
        (offsets, behind) = self.knitter.compute_offsets()

        self.assertEqual(offsets, offset_answer)
        self.assertEqual(behind,  behind_answer)

    def test_decrease_left_then_yarn_over(self):
        pattern = '..\o......'
        offset_answer  = [0, 0, 0, -1, 0] + 5 * [0]
        behind_answer  = [False, False, True, False, False] + 5 * [False]

        knit_pattern(self.knitter, pattern)
        (offsets, behind) = self.knitter.compute_offsets()

        self.assertEqual(offsets, offset_answer)
        self.assertEqual(behind,  behind_answer)

    def test_decrease_right_then_yarn_over(self):
        pattern = '../o......'
        offset_answer  = [0, 0, 0, -1, 0] + 5 * [0]
        behind_answer  = [False, False, False, True, False] + 5 * [False]

        knit_pattern(self.knitter, pattern)
        (offsets, behind) = self.knitter.compute_offsets()

        self.assertEqual(offsets, offset_answer)
        self.assertEqual(behind,  behind_answer)

    def test_center_decrease(self):
        pattern = '.oMo......'
        offset_answer  = [0, 1, 0, -1, 0] + 5 * [0]
        behind_answer  = [False, True, False, True, False] + 5 * [False]

        knit_pattern(self.knitter, pattern)
        (offsets, behind) = self.knitter.compute_offsets()

        self.assertEqual(offsets, offset_answer)
        self.assertEqual(behind,  behind_answer)

    def test_center_decrease(self):
        pattern = '.M.o.o....'
        offset_answer  = [0, 0, -1, -2, -2, -1, 0, 0, 0, 0]
        behind_answer  = [False, False, True, True, False] + 5 * [False]

        knit_pattern(self.knitter, pattern)
        (offsets, behind) = self.knitter.compute_offsets()

        self.assertEqual(offsets, offset_answer)
        self.assertEqual(behind,  behind_answer)

    def tearDown(self):
        self.null.close()

if __name__ == '__main__':
    unittest.main()
