import numpy
from copy import deepcopy
from enum import Enum, IntEnum
from numba import jit, typeof, deferred_type
from numba.experimental import jitclass


class MoveSet(Enum):
    U, M = range(2)


class MoveType(IntEnum):
    Standard, Double, Prime = range(3)


class Pieces(IntEnum):
    UR, UF, UL, UB, DF, DB = range(6)


def convert_move_to_string(move, move_type):
    return ("U" if move == MoveSet.U else "M") + (
        "" if move_type == MoveType.Standard else "2" if move_type == MoveType.Double else "'")


lse_type = deferred_type()


'''@jitclass([
    # Constructor variables
    ('lse_state', lse_type),#LSE_State.class_type.instance_type)
    ('edge_orientation_state', typeof([True])),
    ('edge_permutation_state', typeof(numpy.zeros(1, dtype = int))),
    ('center_AUF_state', typeof(numpy.zeros(1, dtype = int))),
    ('misoriented_centers_orientation_state', typeof([True])),
    ('edge_orientation_state_replacement', typeof([True])),
    ('edge_permutation_state_in_place', typeof(numpy.zeros(1, dtype = int))),
    # toString variables
    ('data', typeof("")),
    # Equality variables
    ('other', lse_type),
    # swap_pieces_permutation method
    ('piece1', typeof(Pieces.UR)),
    ('piece2', typeof(Pieces.UR)),
    # cycle_pieces_permutation method
    ('buffer', typeof(Pieces.UR)),
    ('pieces', typeof((Pieces.UR, Pieces.UL))),
    # apply_move method

])'''
class LSE_State(object):
    def __init__(self, lse_state = None):
        if lse_state is None:
            # Orientation of the piece itself (index 2 = UL edge is oriented if True)
            self.edge_orientation_state = [True for i in range(len(Pieces))]
            # Each number determines which edge is at which location (2 at the 0th index means UL is at UR)
            self.edge_permutation_state = numpy.arange(len(Pieces), dtype = int)
            # U or M increases the value by 1, and prime by 3, etc., mod 4
            self.center_AUF_state = numpy.zeros(2, dtype = int)
            # Orientation of the piece itself (index 2 = UL edge)
            self.misoriented_centers_orientation_state = [True for i in range(len(Pieces))]
            # Orientation of the piece at the location (False at the 0th index means the edge at UR is misoriented)
            self.edge_orientation_state_replacement = [True for i in range(len(Pieces))]
            # The corresponding edge based on index has a number which is where it is (2 at the 0th index means UR is at UL)
            self.edge_permutation_state_in_place = numpy.arange(len(Pieces), dtype = int)
        else:
            self.edge_orientation_state = deepcopy(lse_state.edge_orientation_state)
            self.edge_permutation_state = deepcopy(lse_state.edge_permutation_state)
            self.center_AUF_state = deepcopy(lse_state.center_AUF_state)
            self.misoriented_centers_orientation_state = deepcopy(lse_state.misoriented_centers_orientation_state)
            self.edge_orientation_state_replacement = deepcopy(lse_state.edge_orientation_state_replacement)
            self.edge_permutation_state_in_place = deepcopy(lse_state.edge_permutation_state_in_place)

    def __str__(self):
        data = str(self.edge_orientation_state) + "\n" + str(self.center_AUF_state) + "\nOld: UR UF UL UB DF DB\nNew: "
        for edge in self.edge_permutation_state:
            if edge == 0:
                data += "UR "
            elif edge == 1:
                data += "UF "
            elif edge == 2:
                data += "UL "
            elif edge == 3:
                data += "UB "
            elif edge == 4:
                data += "DF "
            else:
                data += "DB "
        return data

    def __eq__(self, other):
        if type(other) != LSE_State:
            return False

        return self.edge_orientation_state == other.edge_orientation_state and\
               numpy.array_equal(self.edge_permutation_state, other.edge_permutation_state) and\
               numpy.array_equal(self.center_AUF_state, other.center_AUF_state)

    def to_array(self):
        pass

    def swap_pieces_permutation(self, piece1, piece2):
        self.edge_permutation_state[piece1], self.edge_permutation_state[piece2] = self.edge_permutation_state[piece2],\
                                                                                   self.edge_permutation_state[piece1]

    def cycle_pieces_permutation(self, buffer, *pieces):
        for piece in pieces:
            self.swap_pieces_permutation(buffer, piece)

    def apply_move(self, move, move_type):
        if move == MoveSet.U:
            if move_type == MoveType.Standard:
                self.edge_permutation_state[:4] = numpy.roll(self.edge_permutation_state[:4], 1)
                self.center_AUF_state[1] += 1
            elif move_type == MoveType.Double:
                self.edge_permutation_state[:4] = numpy.roll(self.edge_permutation_state[:4], 2)
                self.center_AUF_state[1] += 2
            else:
                self.edge_permutation_state[:4] = numpy.roll(self.edge_permutation_state[:4], -1)
                self.center_AUF_state[1] += 3
        elif move == MoveSet.M:
            if move_type == MoveType.Standard:
                '''
                1) Swap UF and DF
                2) Swap UF and DB
                3) Swap UF and UB
                '''
                self.cycle_pieces_permutation(Pieces.UF, Pieces.DF, Pieces.DB, Pieces.UB)
                self.reorient_middle_slice()
                self.center_AUF_state[0] += 1
            elif move_type == MoveType.Double:
                '''
                1) Swap UF and DB
                2) Swap UB and DF
                '''
                self.swap_pieces_permutation(Pieces.UF, Pieces.DB)
                self.swap_pieces_permutation(Pieces.UB, Pieces.DF)
                self.center_AUF_state[0] += 2
            elif move_type == MoveType.Prime:
                '''
                1) Swap UF and UB
                2) Swap UF and DB
                3) Swap UF and DF
                '''
                self.cycle_pieces_permutation(Pieces.UF, Pieces.UB, Pieces.DB, Pieces.DF)
                self.reorient_middle_slice()
                self.center_AUF_state[0] += 3

        self.center_AUF_state = numpy.remainder(self.center_AUF_state, 4)
        for i in range(len(Pieces)):
            self.misoriented_centers_orientation_state[i] = self.is_lr_edge(Pieces(i)) == self.edge_orientation_state[i]
            self.edge_orientation_state_replacement[i] = self.edge_orientation_state[self.edge_permutation_state[i]]
            #self.edge_permutation_state_in_place[self.edge_permutation_state[i]] = i

    def apply_move_sequence(self, moves):
        for move in moves.split(" "):
            move_set = MoveSet.U if "U" in move else MoveSet.M if "M" in move else None
            if move_set is None:
                return

            move_type = MoveType.Double if "2" in move else MoveType.Prime if "'" in move else MoveType.Standard
            self.apply_move(move_set, move_type)

    def reorient_middle_slice(self):
        uf_index = self.edge_permutation_state[Pieces.UF]
        ub_index = self.edge_permutation_state[Pieces.UB]
        df_index = self.edge_permutation_state[Pieces.DF]
        db_index = self.edge_permutation_state[Pieces.DB]
        self.edge_orientation_state[uf_index] = not self.edge_orientation_state[uf_index]
        self.edge_orientation_state[ub_index] = not self.edge_orientation_state[ub_index]
        self.edge_orientation_state[df_index] = not self.edge_orientation_state[df_index]
        self.edge_orientation_state[db_index] = not self.edge_orientation_state[db_index]

    def is_lr_edge(self, piece):
        return self.edge_permutation_state[piece] == Pieces.UL or self.edge_permutation_state[piece] == Pieces.UR

    def is_solved(self):
        return self.is_oriented() and self.is_permuted() and self.center_AUF_state[0] == 0

    def is_oriented(self):
        return not (False in self.edge_orientation_state)

    def is_misoriented_centers_oriented(self):
        return not (False in self.misoriented_centers_orientation_state)

    def is_permuted(self):
        for i in range(len(self.edge_permutation_state) - 1):
            if self.edge_permutation_state[i] > self.edge_permutation_state[i + 1]:
                return False
        return self.center_AUF_state[1] == 0

    def is_middle_slice_oriented(self):
        return self.center_AUF_state[0] % 2 == 0


if __name__ == '__main__':
    state = LSE_State()
    state.apply_move_sequence("U")
    print(state)
    print(state.edge_permutation_state_in_place)
    print(state.is_solved())
