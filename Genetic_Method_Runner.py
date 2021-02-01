import numpy
import random

method_substeps = 3
permutation_count = 6
orientation_count = 6
center_count = 1
auf_count = 1
center_auf_max = 4


def generate_genetic_sequence():
    chromosome = []
    for i in range((method_substeps - 1) * (3 * (orientation_count - 1))):
        chromosome.append(random.randint(0, 1))
    for i in range((method_substeps - 1) * (2 * (permutation_count - 1))):
        chromosome.append(random.randint(0, 1))
    for i in range((method_substeps - 1) * (center_count + auf_count)):
        chromosome.append(random.randint(0, center_auf_max - 1))

    return numpy.array(chromosome, dtype = int)


'''
The genetic sequence is a list of ((6 - 1) * (2 + 2 + 1) + 2) * 2 = 54 numbers
1) The (6 - 1) factor comes from the 6 edges, minus 1 since the last is predetermined by the 5 other orientations/permutations
2) The * (2 + 2) comes from orientations/permutations of the piece itself, and orientations/permutations of the piece in a particular slot
3) The + 1 comes from misoriented centers orientation
4) The + 2 comes from the center offset and AUF
5) The ) * 2 comes from this being a 3-step process (last step is to solve the rest)

Generally, 0 means arbitrary, 1 means oriented or permuted
'''
if __name__ == '__main__':
    print(generate_genetic_sequence())
