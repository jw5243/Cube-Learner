import numpy
import math
import time
import copy
from enum import Enum, IntEnum
from numba import jit, njit, typeof
from numba.experimental import jitclass


class Move(IntEnum):
    U, U2, U3, M, M2, M3 = range(6)


class Pieces(IntEnum):
    UR, UF, UL, UB, DF, DB = range(6)


#@jitclass(spec = [
#    ('orientation_replaced_by', typeof(numpy.full(len(Pieces), True)))
#])
class LSE_State(object):
    def __init__(self):
        self.orientation_replaced_by = numpy.full(len(Pieces), True)
        self.orientation_carried_to = numpy.full(len(Pieces), True)
        # [UR, UB, UL, DB, UF, DF] from applying M move
        self.permutation_replaced_by = numpy.arange(len(Pieces), dtype = int)
        self.permutation_carried_to = numpy.arange(len(Pieces), dtype = int)

        # [0 1 0 3 1] from applying M move
        self.permutation_condensed = numpy.zeros(len(Pieces) - 1, dtype = int)

        self.auf = 0
        self.center_offset = 0
        self.orientation = 0
        self.permutation = 0

    def __str__(self):
        return str(self.orientation_replaced_by) + "\t" + str(self.permutation_replaced_by) + "\t" + str(self.auf) + "\t" + str(self.center_offset)

    def __eq__(self, other):
        if type(other) != LSE_State:
            return False

        return numpy.array_equal(self.orientation_replaced_by, other.orientation_replaced_by) and \
               numpy.array_equal(self.permutation_replaced_by, other.permutation_replaced_by) and \
               self.auf == other.auf and self.center_offset == other.center_offset

    # if A = self and B = other, then A + B is defined as the permutation/orientation A and then B applied to a solved state
    def __add__(self, other):
        return self

    def extract_orientation_permutation(self):
        orientation_temp = self.orientation
        for i in range(len(Pieces) - 1):
            remainder = orientation_temp % 2
            self.orientation_replaced_by[i] = remainder == 0
            orientation_temp = (orientation_temp - remainder) / 2

        self.orientation_replaced_by[-1] = sum(map(lambda eo: 0 if eo else 1, self.orientation_replaced_by[:-1])) % 2 == 0

        permutation_temp = self.permutation
        i = 1
        while permutation_temp != 0:
            remainder = permutation_temp % i
            self.permutation_condensed[i - 1] = remainder
            permutation_temp = (permutation_temp - remainder) / i
            i += 1

        for i in range(len(self.permutation_condensed)):
            # The index of the permutation_replaced_by array we wish to set
            starting_index = len(Pieces) - i - 1
            # For pieces already set that happen to be greater than the permutation_condensed value, we add to the offset
            offset = 0
            if i != 0:
                pieces_used = numpy.sort(self.permutation_replaced_by[starting_index + 1:])[::-1]
                for piece in pieces_used:
                    if piece >= len(Pieces) - self.permutation_condensed[starting_index - 1] - offset - 1:
                        offset += 1

            # Set permutation to the standard piece shifted by the offset calculated above
            self.permutation_replaced_by[starting_index] = Pieces(len(Pieces) - self.permutation_condensed[starting_index - 1] - offset - 1)

    def update_coordinates(self):
        for i in range(1, len(Pieces)):
            value = 0
            for j in range(0, i):
                if self.permutation_replaced_by[j] > self.permutation_replaced_by[i]:
                    value += 1
            self.permutation_condensed[i - 1] = value

        self.orientation = 0
        self.permutation = 0
        for i in range(len(Pieces) - 1):
            if not self.orientation_replaced_by[i]:
                self.orientation += 2 ** i#(len(Pieces) - i - 2)
            self.permutation += self.permutation_condensed[i] * math.factorial(i)
        self.auf %= 4
        self.center_offset %= 4

    def apply_move(self, move):
        if move == Move.U:
            # UB goes to UR, etc.
            self.permutation_replaced_by[[int(Pieces.UB), int(Pieces.UR), int(Pieces.UF), int(Pieces.UL)]], \
                self.permutation_replaced_by[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]] = \
                self.permutation_replaced_by[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]], \
                self.permutation_replaced_by[[int(Pieces.UB), int(Pieces.UR), int(Pieces.UF), int(Pieces.UL)]]
            self.permutation_carried_to[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]], \
                self.permutation_carried_to[[int(Pieces.UB), int(Pieces.UR), int(Pieces.UF), int(Pieces.UL)]] = \
                self.permutation_carried_to[[int(Pieces.UB), int(Pieces.UR), int(Pieces.UF), int(Pieces.UL)]], \
                self.permutation_carried_to[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]]
            self.auf += 1
        elif move == Move.U2:
            self.permutation_replaced_by[[int(Pieces.UL), int(Pieces.UB), int(Pieces.UR), int(Pieces.UF)]],\
                self.permutation_replaced_by[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]] = \
                self.permutation_replaced_by[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]],\
                self.permutation_replaced_by[[int(Pieces.UL), int(Pieces.UB), int(Pieces.UR), int(Pieces.UF)]]
            self.permutation_carried_to[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]], \
                self.permutation_carried_to[[int(Pieces.UL), int(Pieces.UB), int(Pieces.UR), int(Pieces.UF)]] = \
                self.permutation_carried_to[[int(Pieces.UL), int(Pieces.UB), int(Pieces.UR), int(Pieces.UF)]], \
                self.permutation_carried_to[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]]
            self.auf += 2
        elif move == Move.U3:
            self.permutation_replaced_by[[int(Pieces.UF), int(Pieces.UL), int(Pieces.UB), int(Pieces.UR)]],\
                self.permutation_replaced_by[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]] = \
                self.permutation_replaced_by[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]],\
                self.permutation_replaced_by[[int(Pieces.UF), int(Pieces.UL), int(Pieces.UB), int(Pieces.UR)]]
            self.permutation_carried_to[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]], \
                self.permutation_carried_to[[int(Pieces.UF), int(Pieces.UL), int(Pieces.UB), int(Pieces.UR)]] = \
                self.permutation_carried_to[[int(Pieces.UF), int(Pieces.UL), int(Pieces.UB), int(Pieces.UR)]], \
                self.permutation_carried_to[[int(Pieces.UR), int(Pieces.UF), int(Pieces.UL), int(Pieces.UB)]]
            self.auf += 3
        elif move == Move.M:
            numpy.logical_not(self.orientation_replaced_by, out = self.orientation_replaced_by,
                              where = numpy.array([False, True, False, True, True, True], dtype = bool))
            # UB goes to UF, etc.
            self.permutation_replaced_by[[int(Pieces.UB), int(Pieces.UF), int(Pieces.DF), int(Pieces.DB)]], \
                self.permutation_replaced_by[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]] = \
                self.permutation_replaced_by[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]], \
                self.permutation_replaced_by[[int(Pieces.UB), int(Pieces.UF), int(Pieces.DF), int(Pieces.DB)]]
            self.permutation_carried_to[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]], \
                self.permutation_carried_to[[int(Pieces.UB), int(Pieces.UF), int(Pieces.DF), int(Pieces.DB)]] = \
                self.permutation_carried_to[[int(Pieces.UB), int(Pieces.UF), int(Pieces.DF), int(Pieces.DB)]], \
                self.permutation_carried_to[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]]
            self.center_offset += 1
        elif move == Move.M2:
            self.permutation_replaced_by[[int(Pieces.DB), int(Pieces.UB), int(Pieces.UF), int(Pieces.DF)]], \
                self.permutation_replaced_by[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]] = \
                self.permutation_replaced_by[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]], \
                self.permutation_replaced_by[[int(Pieces.DB), int(Pieces.UB), int(Pieces.UF), int(Pieces.DF)]]
            self.permutation_carried_to[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]], \
                self.permutation_carried_to[[int(Pieces.DB), int(Pieces.UB), int(Pieces.UF), int(Pieces.DF)]] = \
                self.permutation_carried_to[[int(Pieces.DB), int(Pieces.UB), int(Pieces.UF), int(Pieces.DF)]], \
                self.permutation_carried_to[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]]
            self.center_offset += 2
        elif move == Move.M3:
            numpy.logical_not(self.orientation_replaced_by, out = self.orientation_replaced_by,
                              where = numpy.array([False, True, False, True, True, True], dtype = bool))
            self.permutation_replaced_by[[int(Pieces.DF), int(Pieces.DB), int(Pieces.UB), int(Pieces.UF)]], \
                self.permutation_replaced_by[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]] = \
                self.permutation_replaced_by[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]], \
                self.permutation_replaced_by[[int(Pieces.DF), int(Pieces.DB), int(Pieces.UB), int(Pieces.UF)]]
            self.permutation_carried_to[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]], \
                self.permutation_carried_to[[int(Pieces.DF), int(Pieces.DB), int(Pieces.UB), int(Pieces.UF)]] = \
                self.permutation_carried_to[[int(Pieces.DF), int(Pieces.DB), int(Pieces.UB), int(Pieces.UF)]], \
                self.permutation_carried_to[[int(Pieces.UF), int(Pieces.DF), int(Pieces.DB), int(Pieces.UB)]]
            self.center_offset += 3
        self.update_coordinates()


if __name__ == '__main__':
    solved_state = LSE_State()
    lse_state = LSE_State()
    lse_state.apply_move(Move.M)
    lse_state.apply_move(Move.M)
    lse_state.apply_move(Move.M3)
    lse_state.apply_move(Move.M3)
    print(solved_state)
    print(lse_state)
    print(solved_state == lse_state)
    print(lse_state.orientation)
    print(lse_state.permutation)
    lse_state.extract_orientation_permutation()
    print(lse_state)
