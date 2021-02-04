import numpy
from LSE_State import *
from Algorithm import *
import LSE_Solver

prune_table = [[[Algorithm(""), LSE_State()]]]
move_set_list = list(MoveSet)
move_type_list = list(MoveType)


def prune_lse_states_at_depth(depth):
    pruned_data = []
    if depth == 1:
        for move in move_set_list:
            for move_type in move_type_list:
                current_state = LSE_State(prune_table[0][0][1])
                current_state.apply_move(move, move_type)
                pruned_data.append([Algorithm(convert_move_to_string(move, move_type)), current_state])
    else:
        for pruned_state in prune_table[depth - 1]:
            for move_type in move_type_list:
                move = MoveSet.U if LSE_Solver.get_last_move(pruned_state[0].algorithm)[0] == MoveSet.M else MoveSet.M
                current_state = LSE_State(pruned_state[1])
                current_state.apply_move(move, move_type)
                pruned_data.append(
                    [Algorithm(pruned_state[0].algorithm + " " + convert_move_to_string(move, move_type)), current_state])
    prune_table.append(pruned_data)


def prune_lse_states(depth):
    for i in range(1, depth + 1):
        print("Pruning at depth... " + str(i))
        prune_lse_states_at_depth(i)
    print("Finished pruning")


if __name__ == '__main__':
    depth = 9
    prune_lse_states(depth)
    for prune_table_at_depth in prune_table:
        for pruned_state in prune_table_at_depth:
            print(str(pruned_state[0])) #+ "\t" + str(pruned_state[1]))
