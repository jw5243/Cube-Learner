import numpy
import random
import copy
from LSE_Solver import *
from LSE_State import *

method_substeps = 3
permutation_count = 6
orientation_count = 6
center_count = 1
auf_count = 1
center_auf_max = 4

max_generations = 1#10
population_size = 2
elitism_count = 2
crossover_probability = 0.9
mutation_probability = 0.1

max_cost = 5000
current_generation = 1

chromosome_length = (method_substeps - 1) * (2 * (orientation_count - 1) + permutation_count + center_count + auf_count)

population = []
next_population = []
costs = []

scrambles_to_test = 10


def generate_chromosome():
    chromosome = []
    '''for i in range((method_substeps - 1) * (2 * (orientation_count - 1))):
        chromosome.append(get_random_tune_value(2))
    #for i in range((method_substeps - 1) * (2 * (permutation_count - 1))):
    #    chromosome.append(get_random_tune_value(2))
    for i in range(method_substeps - 1):
        permutation = numpy.random.permutation(5)
        genome_sequence = []
        for j in range(permutation_count - 1):
            random_value = get_random_tune_value(6)
            if random_value == 6:
                genome_sequence.append(random_value)
            else:
                genome_sequence.append(permutation[j])
        chromosome.extend(genome_sequence)
    for i in range((method_substeps - 1) * (center_count + auf_count)):
        chromosome.append(get_random_tune_value(center_auf_max - 1 + 1))'''
    permutations = []
    for i in range(method_substeps - 1):
        permutation = numpy.random.permutation(6)
        genome_sequence = []
        for j in range(permutation_count):
            random_value = random.randint(0, 9)
            genome_sequence.append(random_value if random_value == 6 else permutation[j])
        permutations.extend(genome_sequence)
    print(permutations)
    for i in range(chromosome_length):
        if i < (method_substeps - 1) * (2 * (orientation_count - 1)) or i >= (method_substeps - 1) * (2 * (orientation_count - 1) + permutation_count):
            gene = get_random_tune_value(i)
        else:
            gene = permutations[0]
            permutations = permutations[1:]
        chromosome.append(gene)

    chromosome = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                  9, 9, 9, 9, 6, 6, 0, 9, 2, 9, 9, 9,
                  6, 5, 6, 5]

    return numpy.array(chromosome, dtype = int)


def crosover(index1, index2):
    crossover_index = random.randint(1, chromosome_length - 2)
    print("Crossing over chromosomes " + str(index1) + " and " + str(index2) + " at index " + str(crossover_index))
    next_population.append(copy.deepcopy(population[index1]))
    next_population.append(copy.deepcopy(population[index2]))
    for i in range(crossover_index):
        next_population[-1][i], next_population[-2][i] = next_population[-2][i], next_population[-1][i]


def mutation(current_index):
    index = get_random_gene_index()
    print("Mutating chromosome " + str(current_index) + " at index " + str(index))
    next_population.append(copy.deepcopy(population[current_index]))
    #TODO: Fix tune value maximum
    next_population[-1][index] = get_random_tune_value(
        1 if (index < chromosome_length - center_count + auf_count) else center_auf_max - 1)


def get_random_gene_index():
    return random.randint(0, chromosome_length - 1)


def get_random_chromosome_index():
    total_cost = sum(costs)
    total_normalized_probability = sum(map(lambda cost: (total_cost - cost)**2, costs))
    selection_probability = list(map(lambda cost: (total_cost - cost)**2 / total_normalized_probability, costs))
    random_value = random.random()
    current_probability_sum = 0
    for i in range(len(selection_probability)):
        if selection_probability[i] + current_probability_sum > random_value >= current_probability_sum:
            return i
        current_probability_sum += selection_probability[i]
    return chromosome_length - 1


def get_random_tune_value(index):#max_value):
    #return random.randint(0, max_value)
    if index < (method_substeps - 1) * (2 * (orientation_count - 1)):
        return random.randint(0, 2)
    elif index < (method_substeps - 1) * (2 * (orientation_count - 1) + permutation_count - 1):
        return random.randint(0, 9)
    else:
        return random.randint(0, center_auf_max)

def simulate_generation():
    global population, next_population, current_generation, costs
    if current_generation == 1:
        for i in range(population_size):
            population.append(generate_chromosome())
            costs.append(max_cost)
    else:
        k = elitism_count
        sorted_population = [x for _, x in sorted(zip(costs, population), key = lambda pair: pair[0])]
        next_population = []
        for i in range(k):
            next_population.append(sorted_population[i])

        while k < population_size:
            generation_transition_type = random.random()
            if generation_transition_type <= crossover_probability and k < population_size - 2:
                index1 = get_random_chromosome_index()
                index2 = get_random_chromosome_index()
                while index1 == index2:
                    index2 = get_random_chromosome_index()
                crosover(index1, index2)
                k += 1
            else:
                index = get_random_chromosome_index()
                mutation(index)
            k += 1
        population = next_population
    costs = []
    for chromosome in population:
        run_iteration(chromosome)
    current_generation += 1


def run_iteration(chromosome):
    print(chromosome)
    total_cost = 0
    for i in range(scrambles_to_test):
        solution = Algorithm("")
        solution_substeps = []
        solved = True
        substeps_used = 0
        scramble = generate_random_scramble(15)
        print("Scramble: " + str(scramble.algorithm))
        solved_states = search_solutions(scramble.algorithm, 9,
                                         lambda state: check_substep_criteria(chromosome, 1, state), max_solutions = 1, debug = False)
        cost = get_cost(solved_states)
        if len(solved_states) != 0:
            substeps_used += 1
            total_cost += cost
            scramble.append_algorithm(solved_states[0][0])
            solution.append_algorithm(solved_states[0][0])
            solution_substeps.append(solved_states[0][0])
        solved_states = search_solutions(scramble.algorithm, 9,
                                         lambda state: check_substep_criteria(chromosome, 2, state), max_solutions = 1, debug = False)
        cost = get_cost(solved_states)
        if len(solved_states) != 0:
            substeps_used += 1
            total_cost += cost
            scramble.append_algorithm(solved_states[0][0])
            solution.append_algorithm(solved_states[0][0])
            solution_substeps.append(solved_states[0][0])
        solved_states = search_solutions(scramble.algorithm, 9, lambda state: state == SOLVED_STATE, max_solutions = 1, debug = False)
        cost = get_cost(solved_states)
        if len(solved_states) != 0 and substeps_used > 0:
            total_cost += cost
            scramble.append_algorithm(solved_states[0][0])
            solution.append_algorithm(solved_states[0][0])
            solution_substeps.append(solved_states[0][0])
        else:
            total_cost += max_cost
            solved = False

        if solved:
            for i in range(len(solution_substeps)):
                print("Step " + str(i) + ": " + str(solution_substeps[i]))
            print("Full Solution: " + str(solution))
        else:
            print("Failed to find solution")
    costs.append(total_cost)
    print(costs)


def get_cost(solved_states):
    #M3U_tps = 12.9
    #M3U2_tps = 10.4
    #M3U3_tps = 8.4
    return max_cost if len(solved_states) == 0 else min(solved_states, key = lambda state: state[0].move_count)[0].move_count


def check_substep_criteria(chromosome, substep, state):
    if substep == 1:
        for i in range(orientation_count - 1):
            if chromosome[i] == 1:
                if not state.edge_orientation_state[i]:
                    return False
            elif chromosome[i] == 2:
                if state.edge_orientation_state[i]:
                    return False
        for i in range(orientation_count - 1, 2 * (orientation_count - 1)):
            if chromosome[i] == 1:
                if not state.edge_orientation_state_replacement[i - (orientation_count - 1)]:
                    return False
            elif chromosome[i] == 2:
                if state.edge_orientation_state_replacement[i - (orientation_count - 1)]:
                    return False
        for j in range(4 * (orientation_count - 1), 4 * (orientation_count - 1) + permutation_count):
            edge_permutation_state = state.edge_permutation_state[j - 4 * (orientation_count - 1)]
            if chromosome[j] < 6:
                if not edge_permutation_state == chromosome[j]:
                    return False
            elif chromosome[j] == 6:
                if not (edge_permutation_state == int(Pieces.UL) or edge_permutation_state == int(Pieces.UR)):
                    return False
            elif chromosome[j] == 7:
                if not (edge_permutation_state == int(Pieces.UF) or edge_permutation_state == int(Pieces.UB)):
                    return False
            elif chromosome[j] == 8:
                if not (edge_permutation_state == int(Pieces.DF) or edge_permutation_state == int(Pieces.DB)):
                    return False
        if chromosome[-4] < 4:
            if state.center_AUF_state[0] != chromosome[-4]:
                return False
        elif chromosome[-4] == 6:
            if not state.is_middle_slice_oriented():
                return False
        if chromosome[-3] < 4:
            if state.center_AUF_state[1] != chromosome[-3]:
                return False
    elif substep == 2:
        for i in range(2 * (orientation_count - 1), 3 * (orientation_count - 1)):
            if chromosome[i] == 1:
                if not state.edge_orientation_state[i - 2 * (orientation_count - 1)]:
                    return False
            elif chromosome[i] == 2:
                if state.edge_orientation_state[i - 2 * (orientation_count - 1)]:
                    return False
        for i in range(3 * (orientation_count - 1), 4 * (orientation_count - 1)):
            if chromosome[i] == 1:
                if not state.edge_orientation_state_replacement[i - 3 * (orientation_count - 1)]:
                    return False
            elif chromosome[i] == 2:
                if state.edge_orientation_state_replacement[i - 3 * (orientation_count - 1)]:
                    return False
        for j in range(4 * (orientation_count - 1) + permutation_count, 4 * (orientation_count - 1) + 2 * permutation_count):
            edge_permutation_state = state.edge_permutation_state[j - (4 * (orientation_count - 1) + permutation_count)]
            if chromosome[j] < 6:
                if not edge_permutation_state == chromosome[j]:
                    return False
            elif chromosome[j] == 6:
                if not (edge_permutation_state == int(Pieces.UL) or edge_permutation_state == int(Pieces.UR)):
                    return False
            elif chromosome[j] == 7:
                if not (edge_permutation_state == int(Pieces.UF) or edge_permutation_state == int(Pieces.UB)):
                    return False
            elif chromosome[j] == 8:
                if not (edge_permutation_state == int(Pieces.DF) or edge_permutation_state == int(Pieces.DB)):
                    return False
        if chromosome[-2] < 4:
            if state.center_AUF_state[0] != chromosome[-2]:
                return False
        elif chromosome[-2] == 6:
            if not state.is_middle_slice_oriented():
                return False
        if chromosome[-1] < 4:
            if state.center_AUF_state[1] != chromosome[-1]:
                return False
    return True


'''
The genetic sequence is a list of ((6 - 1) * (2 + 2 + 1) + 2) * 2 = 54 numbers
1) The (6 - 1) factor comes from the 6 edges, minus 1 since the last is predetermined by the 5 other orientations/permutations
2) The * (2 + 2) comes from orientations/permutations of the piece itself, and orientations/permutations of the piece in a particular slot
3) The + 1 comes from misoriented centers orientation
4) The + 2 comes from the center offset and AUF
5) The ) * 2 comes from this being a 3-step process (last step is to solve the rest)

Generally, 0 means arbitrary, 1 means oriented or permuted, 2 means not oriented or not permuted 
5 means does not matter and 6 means oriented for center and AUF
6, 7, 8 means either UL/UR, UF/UB, DF/DB are permuted in the associated position, respectively (9 being does not matter)

[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
 9, 9, 9, 9, 6, 6, 0, 9, 2, 9, 9, 9,
 6, 5, 6, 5]
 
The first 5 numbers represent the edge orientation (in place), the next 5 the edge orientation (replacement),
with the rest of the 10 numbers the same thing for the second substep. Starting with the next row, the first 5 numbers
represent the edge permutation (replacement), and the next 5 the edge permutation for the next substep

This example is EOLR + 4c
'''
if __name__ == '__main__':
    simulate_generation()
