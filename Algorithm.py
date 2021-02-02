import copy


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
        if self.move_count > 0:
            self.algorithm += " " + algorithm.algorithm
        else:
            self.algorithm += algorithm.algorithm
        self.algorithm_by_moves.extend(algorithm.algorithm_by_moves)
        self.inverted_algorithm_by_moves = copy.deepcopy(self.algorithm_by_moves)
        self.inverted_algorithm_by_moves.reverse()
        self.move_count += algorithm.move_count
        self.algorithm_inverted = self.invert_algorithm()
