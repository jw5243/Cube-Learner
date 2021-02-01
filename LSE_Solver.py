import numpy
import time
from LSE_State import *
from Algorithm import *

SOLVED_STATE = LSE_State()


def get_last_move(solution):
    move = solution.split(" ")[-1]
    return [MoveSet.U if "U" in move else MoveSet.M,
            MoveType.Double if "2" in move else MoveType.Prime if "'" in move else MoveType.Standard]


def search_solutions(scramble, depth, criterion):
    scrambled_state = LSE_State(SOLVED_STATE)
    scrambled_state.apply_move_sequence(scramble)
    move_set_list = list(MoveSet)
    move_type_list = list(MoveType)
    previous_states = []
    states = []
    for i in range(depth):
        print("Searching depth... " + str(i))
        if i == 0:
            for move in move_set_list:
                for move_type in move_type_list:
                    current_state = LSE_State(scrambled_state)
                    current_state.apply_move(move, move_type)
                    states.append([convert_move_to_string(move, move_type), current_state])
                    if criterion(current_state):
                        print(states[-1][0])
        else:
            for previous_state in previous_states:
                for move_type in move_type_list:
                    move = MoveSet.U if get_last_move(previous_state[0])[0] == MoveSet.M else MoveSet.M
                    current_state = LSE_State(previous_state[1])
                    current_state.apply_move(move, move_type)
                    states.append([previous_state[0] + " " + convert_move_to_string(move, move_type), current_state])
                    if criterion(current_state):
                        print(states[-1][0])
        previous_states = states
        states = []


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
