from numba import jit, typeof
from numba.experimental import jitclass
from enum import Enum, IntEnum
from LSE_State import MoveSet
import time


class MoveSet(Enum):
    U, M = range(2)


#@jitclass([
#    ('move', typeof(MoveSet.U))
#])
class Test(object):
    def __init__(self):
        pass

    @staticmethod
    @jit(nopython = True)
    def test_method(move):
        if move == MoveSet.U:
            return 1
            #print("Hi")


if __name__ == '__main__':
    Test.test_method(MoveSet.U)
    loop_count = 1000
    total_time = 0
    for i in range(loop_count):
        start = time.time()
        Test.test_method(MoveSet.U)
        total_time += time.time() - start
    print(total_time / loop_count)
