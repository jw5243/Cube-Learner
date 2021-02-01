import copy


class Algorithm(object):
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.algorithm_by_moves = algorithm.split(" ")
        self.inverted_algorithm_by_moves = copy.deepcopy(self.algorithm_by_moves)
        self.inverted_algorithm_by_moves.reverse()
        self.move_count = len(self.algorithm_by_moves) if algorithm != "" else 0
        self.algorithm_inverted = self.invert_algorithm(algorithm)

    def __str__(self):
        return "Move Count = " + str(self.move_count) + ": " + self.algorithm

    def invert_algorithm(self, algorithm = ""):
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
