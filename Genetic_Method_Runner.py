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

max_generations = 10
population_size = 5
elitism_count = 2
crossover_probability = 0.9
mutation_probability = 0.1

max_cost = 5000
current_generation = 1

chromosome_length = (method_substeps - 1) * (2 * (orientation_count + permutation_count - 2) + center_count + auf_count)

population = []
next_population = []
costs = []

scrambles_to_test = 10


def generate_chromosome():
    chromosome = []
    for i in range((method_substeps - 1) * (orientation_count - 1)):#(2 * (orientation_count - 1))):
        chromosome.append(get_random_tune_value(2))
    for i in range((method_substeps - 1) * (orientation_count - 1)):#(2 * (permutation_count - 1))):
        chromosome.append(get_random_tune_value(2))
    for i in range((method_substeps - 1) * (center_count + auf_count)):
        chromosome.append(get_random_tune_value(center_auf_max - 1))

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


def get_random_tune_value(max_value):
    return random.randint(0, max_value)


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
        solved_states = search_solutions(generate_random_scramble(10).algorithm, 9,
                                         lambda state: check_substep_criteria(population[i], 1, state), debug = True)
        cost = get_cost(solved_states)
        print(cost)
        total_cost += cost
        solved_states = search_solutions(generate_random_scramble(10).algorithm, 9,
                                         lambda state: check_substep_criteria(population[i], 2, state))
        cost = get_cost(solved_states)
        print(cost)
        total_cost += cost
        solved_states = search_solutions(generate_random_scramble(5).algorithm, 9, lambda state: state == SOLVED_STATE)
        cost = get_cost(solved_states)
        print(cost)
        total_cost += cost
    costs.append(total_cost)


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
        for j in range(2 * (orientation_count - 1), 2 * (orientation_count - 1) + permutation_count - 1):
            if chromosome[j] == 1:
                if not state.edge_permutation_state[j - 2 * (orientation_count - 1)] == j - 2 * (orientation_count - 1):
                    return False
            elif chromosome[j] == 2:
                if state.edge_permutation_state[j - 2 * (orientation_count - 1)] == j - 2 * (orientation_count - 1):
                    return False
        if chromosome[-4] < 4:
            if state.center_AUF_state[0] != chromosome[-4]:
                return False
        if chromosome[-3] < 4:
            if state.center_AUF_state[1] != chromosome[-3]:
                return False
    elif substep == 2:
        for i in range(orientation_count - 1, 2 * (orientation_count - 1)):
            if chromosome[i] == 1:
                if not state.edge_orientation_state[i - (orientation_count - 1)]:
                    return False
            elif chromosome[i] == 2:
                if state.edge_orientation_state[i - (orientation_count - 1)]:
                    return False
        for j in range(2 * (orientation_count - 1) + permutation_count - 1, 2 * (orientation_count - 1) + 2 * (permutation_count - 1)):
            if chromosome[j] == 1:
                if not state.edge_permutation_state[j - 2 * (orientation_count - 1) - permutation_count - 1] == \
                       2 * (orientation_count - 1) + permutation_count - 1:
                    return False
            elif chromosome[j] == 2:
                if state.edge_permutation_state[j - 2 * (orientation_count - 1) - permutation_count - 1] == \
                       2 * (orientation_count - 1) + permutation_count - 1:
                    return False
        if chromosome[-2] < 4:
            if state.center_AUF_state[0] != chromosome[-2]:
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
'''
if __name__ == '__main__':
    simulate_generation()
    simulate_generation()
    print(population)
