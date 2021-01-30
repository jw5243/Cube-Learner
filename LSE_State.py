import numpy
from copy import deepcopy
from enum import Enum


class MoveSet(Enum):
    U, M = range(2)


class MoveType(Enum):
    Standard, Double, Prime = range(3)


class Pieces(Enum):
    UR, UF, UL, UB, DF, DB = range(6)


def convert_move_to_string(move, move_type):
    return ("U" if move == MoveSet.U else "M") + ("" if move_type == MoveType.Standard else "2" if move_type == MoveType.Double else "'")


class LSE_State(object):
    def __init__(self, lse_state = None):
        if lse_state is None:
            self.edge_orientation_state = [True for i in range(len(Pieces))]
            self.edge_permutation_state = numpy.arange(len(Pieces), dtype = int)
            self.center_AUF_state = numpy.zeros(2, dtype = int)
        else:
            self.edge_orientation_state = deepcopy(lse_state.edge_orientation_state)
            self.edge_permutation_state = deepcopy(lse_state.edge_permutation_state)
            self.center_AUF_state = deepcopy(lse_state.center_AUF_state)

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

        return self.edge_orientation_state == other.edge_orientation_state and \
               numpy.array_equal(self.edge_permutation_state, other.edge_permutation_state) and \
               numpy.array_equal(self.center_AUF_state, other.center_AUF_state)

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
                self.edge_permutation_state[1], self.edge_permutation_state[4] = self.edge_permutation_state[4], \
                                                                                 self.edge_permutation_state[1]
                self.edge_permutation_state[1], self.edge_permutation_state[5] = self.edge_permutation_state[5],\
                                                                                 self.edge_permutation_state[1]
                self.edge_permutation_state[1], self.edge_permutation_state[3] = self.edge_permutation_state[3],\
                                                                                 self.edge_permutation_state[1]
                uf_index = self.edge_permutation_state[1]
                ub_index = self.edge_permutation_state[3]
                df_index = self.edge_permutation_state[4]
                db_index = self.edge_permutation_state[5]
                self.edge_orientation_state[uf_index] = not self.edge_orientation_state[uf_index]
                self.edge_orientation_state[ub_index] = not self.edge_orientation_state[ub_index]
                self.edge_orientation_state[df_index] = not self.edge_orientation_state[df_index]
                self.edge_orientation_state[db_index] = not self.edge_orientation_state[db_index]
                self.center_AUF_state[0] += 1
            elif move_type == MoveType.Double:
                '''
                1) Swap UF and DB
                2) Swap UB and DF
                '''
                self.edge_permutation_state[1], self.edge_permutation_state[5] = self.edge_permutation_state[5],\
                                                                                 self.edge_permutation_state[1]
                self.edge_permutation_state[3], self.edge_permutation_state[4] = self.edge_permutation_state[4],\
                                                                                 self.edge_permutation_state[3]
                self.center_AUF_state[0] += 2
            else:
                '''
                1) Swap UF and UB
                2) Swap UF and DB
                3) Swap UF and DF
                '''
                self.edge_permutation_state[1], self.edge_permutation_state[3] = self.edge_permutation_state[3],\
                                                                                 self.edge_permutation_state[1]
                self.edge_permutation_state[1], self.edge_permutation_state[5] = self.edge_permutation_state[5],\
                                                                                 self.edge_permutation_state[1]
                self.edge_permutation_state[1], self.edge_permutation_state[4] = self.edge_permutation_state[4],\
                                                                                 self.edge_permutation_state[1]
                uf_index = self.edge_permutation_state[1]
                ub_index = self.edge_permutation_state[3]
                df_index = self.edge_permutation_state[4]
                db_index = self.edge_permutation_state[5]
                self.edge_orientation_state[uf_index] = not self.edge_orientation_state[uf_index]
                self.edge_orientation_state[ub_index] = not self.edge_orientation_state[ub_index]
                self.edge_orientation_state[df_index] = not self.edge_orientation_state[df_index]
                self.edge_orientation_state[db_index] = not self.edge_orientation_state[db_index]
                self.center_AUF_state[0] += 3

        self.center_AUF_state = numpy.remainder(self.center_AUF_state, 4)

    def apply_move_sequence(self, moves = ""):
        for move in moves.split(" "):
            if "U" in move:
                if "2" in move:
                    self.apply_move(MoveSet.U, MoveType.Double)
                elif "'" in move:
                    self.apply_move(MoveSet.U, MoveType.Prime)
                else:
                    self.apply_move(MoveSet.U, MoveType.Standard)
            elif "M" in move:
                if "2" in move:
                    self.apply_move(MoveSet.M, MoveType.Double)
                elif "'" in move:
                    self.apply_move(MoveSet.M, MoveType.Prime)
                else:
                    self.apply_move(MoveSet.M, MoveType.Standard)

    def is_solved(self):
        if False in self.edge_orientation_state:
            return False
        for i in range(len(self.edge_permutation_state) - 1):
            if self.edge_permutation_state[i] > self.edge_permutation_state[i + 1]:
                return False
        return not self.center_AUF_state.any()


if __name__ == '__main__':
    state = LSE_State()
    state.apply_move_sequence("U M M' U'")
    print(state)
    print(state.is_solved())
