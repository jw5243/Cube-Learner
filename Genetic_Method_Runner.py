import numpy


def generate_genetic_sequence():
    pass


'''
The genetic sequence is a list of ((6 - 1) * (2 + 2 + 1) + 2) * 2 = 54 numbers
1) The (6 - 1) factor comes from the 6 edges, minus 1 since the last is predetermined by the 5 other orientations/permutations
2) The * (2 + 2) comes from permutation/orientation of the piece itself, and permutation/orientation of the piece in a particular slot
3) The + 1 comes from misoriented centers orientation
4) The + 2 comes from the center offset and AUF
5) The ) * 2 comes from this being a 3-step process (last step is to solve the rest)
'''
if __name__ == '__main__':
    method_substeps = 3
    permutation_count = 6
    orientation_count = 6
    center_count = 1
    auf_count = 1
    center_auf_max = 4
