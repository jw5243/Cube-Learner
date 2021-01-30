import numpy
import time
from LSE_State import *

SOLVED_STATE = LSE_State()


def get_last_move(solution):
    move = solution.split(" ")[-1]
    return [MoveSet.U if "U" in move else MoveSet.M, MoveType.Double if "2" in move else MoveType.Prime if "'" in move else MoveType.Standard]


def search_solution_depth(scramble, depth):
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
                    if current_state == SOLVED_STATE:
                        print(states[-1][0])
        else:
            for previous_state in previous_states:
                for move_type in move_type_list:
                    move = MoveSet.U if get_last_move(previous_state[0])[0] == MoveSet.M else MoveSet.M
                    current_state = LSE_State(previous_state[1])
                    current_state.apply_move(move, move_type)
                    states.append([previous_state[0] + " " + convert_move_to_string(move, move_type), current_state])
                    if current_state == SOLVED_STATE:
                        print(states[-1][0])
        previous_states = states
        states = []
        #print(previous_states)


if __name__ == '__main__':
    scramble = "M2 U2 M2"
    max_length = 10
    start_time = time.time()
    search_solution_depth(scramble, max_length)
    print(time.time() - start_time)
