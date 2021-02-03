import copy
from LSE_State import *


class Algorithm(object):
    def __init__(self, algorithm = None, algorithm_by_moves = None):
        if algorithm is not None:
            self.algorithm = algorithm
            self.algorithm_by_moves = algorithm.split(" ")
        elif algorithm_by_moves is not None:
            self.algorithm_by_moves = algorithm_by_moves
            self.algorithm = ""
            for i in range(len(self.algorithm_by_moves)):
                self.algorithm += self.algorithm_by_moves[i]
                if i < len(self.algorithm_by_moves) - 1:
                    self.algorithm += " "
        else:
            pass
        self.inverted_algorithm_by_moves = copy.deepcopy(self.algorithm_by_moves)
        self.inverted_algorithm_by_moves.reverse()
        self.move_count = len(self.algorithm_by_moves) if algorithm != "" else 0
        self.algorithm_inverted = self.invert_algorithm()

    def __str__(self):
        return "Move Count = " + str(self.move_count) + ": " + self.algorithm

    def invert_algorithm(self):
        inverted_algorithm = ""
        for i in range(self.move_count):
            if "'" in self.inverted_algorithm_by_moves[i]:
                inverted_algorithm += self.inverted_algorithm_by_moves[i][:-1]
            elif "2" not in self.inverted_algorithm_by_moves[i]:
                inverted_algorithm += self.inverted_algorithm_by_moves[i] + "'"
            else:
                inverted_algorithm += self.inverted_algorithm_by_moves[i]

            if i < len(self.inverted_algorithm_by_moves) - 1:
                inverted_algorithm += " "
        return inverted_algorithm

    def append_algorithm(self, algorithm):
        join_amount = 0
        joining_move1 = self.get_move(-1)
        joining_move2 = algorithm.get_move(0)
        combined = False
        while joining_move1[0] == joining_move2[0]:
            combined = True
            self.algorithm_by_moves = self.algorithm_by_moves[:-1]
            joining_move1 = self.get_move(-1 - join_amount)
            joining_move2 = algorithm.get_move(join_amount)
            move_distance = (2 + int(joining_move1[1]) + int(joining_move2[1])) % 4
            if move_distance == 0:
                self.move_count -= 2
                join_amount += 1
            else:
                combined_move = [joining_move1[0], MoveType(move_distance - 1)]
                combined_move_string = convert_move_to_string(combined_move[0], combined_move[1])
                self.algorithm_by_moves.append(combined_move_string)
                self.move_count -= 1
                self.algorithm_by_moves.extend(algorithm.algorithm_by_moves[1 + join_amount:])
                self.algorithm = ""
                for i in range(len(self.algorithm_by_moves)):
                    self.algorithm += self.algorithm_by_moves[i]
                    if i < len(self.algorithm_by_moves) - 1:
                        self.algorithm += " "
                break
        if not combined:
            if self.move_count > 0:
                self.algorithm += " " + algorithm.algorithm
            else:
                self.algorithm += algorithm.algorithm
            self.algorithm_by_moves.extend(algorithm.algorithm_by_moves)
        self.inverted_algorithm_by_moves = copy.deepcopy(self.algorithm_by_moves)
        self.inverted_algorithm_by_moves.reverse()
        self.move_count += algorithm.move_count
        self.algorithm_inverted = self.invert_algorithm()

    def get_move(self, index):
        #if index >= 0:
        move = self.algorithm.split(" ")[index]
        return [MoveSet.U if "U" in move else MoveSet.M,
                MoveType.Double if "2" in move else MoveType.Prime if "'" in move else MoveType.Standard]
        #return [None, None]


if __name__ == '__main__':
    algorithm = Algorithm("M' U' M' U' M' U M")
    algorithm2 = Algorithm("M2 U'")
    algorithm3 = Algorithm("U M2 U2 M2 U' M2")
    print(algorithm)
    algorithm.append_algorithm(algorithm2)
    print(algorithm)
    algorithm.append_algorithm(algorithm3)
    print(algorithm)
