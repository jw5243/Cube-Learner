import numpy
import time
import random
from LSE_State import *
from Algorithm import *

SOLVED_STATE = LSE_State()


def generate_random_scramble(length):
    scramble = ""
    move_set_list = list(MoveSet)
    move_type_list = list(MoveType)
    move_set_value = random.randint(0, len(move_set_list) - 1)
    for i in range(length):
        move_type_value = random.randint(0, len(move_type_list) - 1)
        scramble += ("U" if move_set_value % 2 == 0 else "M") + ("2 " if move_type_value == 0 else "' " if move_type_value == 1 else " ")
        move_set_value += 1
    return Algorithm(scramble[:-1])


def get_last_move(solution):
    move = solution.split(" ")[-1]
    return [MoveSet.U if "U" in move else MoveSet.M,
            MoveType.Double if "2" in move else MoveType.Prime if "'" in move else MoveType.Standard]


def search_solutions(scramble, depth, criterion, max_solutions = 10000, debug = False):
    if debug:
        print(scramble)
    solved_states = []
    scrambled_state = LSE_State(SOLVED_STATE)
    scrambled_state.apply_move_sequence(scramble)
    if criterion(scrambled_state):
        solved_states.append([Algorithm(""), scrambled_state])
        if debug:
            print("Skip!")
    move_set_list = list(MoveSet)
    move_type_list = list(MoveType)
    previous_states = []
    states = []
    for i in range(depth):
        if debug:
            print("Searching depth... " + str(i))
        if i == 0:
            for move in move_set_list:
                for move_type in move_type_list:
                    current_state = LSE_State(scrambled_state)
                    current_state.apply_move(move, move_type)
                    states.append([convert_move_to_string(move, move_type), current_state])
                    if criterion(current_state):
                        solved_states.append([Algorithm(convert_move_to_string(move, move_type)), current_state])
                        if debug:
                            print(states[-1][0])
                        if len(solved_states) > max_solutions:
                            return solved_states
        else:
            for previous_state in previous_states:
                for move_type in move_type_list:
                    move = MoveSet.U if get_last_move(previous_state[0])[0] == MoveSet.M else MoveSet.M
                    current_state = LSE_State(previous_state[1])
                    current_state.apply_move(move, move_type)
                    states.append([previous_state[0] + " " + convert_move_to_string(move, move_type), current_state])
                    if criterion(current_state):
                        solved_states.append([Algorithm(previous_state[0] + " " + convert_move_to_string(move, move_type)), current_state])
                        if debug:
                            print(states[-1][0])
                        if len(solved_states) > max_solutions:
                            return solved_states
        previous_states = states
        states = []
    return solved_states


def search_solved_state(scramble, depth):
    search_solutions(scramble, depth, lambda current_state: current_state == SOLVED_STATE)


def search_oriented_state(scramble, depth):
    search_solutions(scramble, depth, lambda current_state: current_state.is_oriented())


if __name__ == '__main__':
    scramble = "M' U2 M2 U2 M"
    max_length = 5
    start_time = time.time()
    search_oriented_state(scramble, max_length)
    #search_solved_state(scramble, max_length)
    print(time.time() - start_time)
