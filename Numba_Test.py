from numba import jit, typeof
from numba.experimental import jitclass
import time
import numpy
import dis


test_vector = numpy.arange(4)
test_array = numpy.array([
    [0, 1, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]], dtype = int
)


#@jitclass([
#    ('move', typeof(MoveSet.U))
#])
class Test(object):
    def __init__(self):
        self.test_vector = numpy.arange(4)
        self.test_array = numpy.array([
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]], dtype = int
        )

    #@staticmethod
    @jit(nopython = True)
    def test_method(self):
        self.test_vector = self.test_array * self.test_vector


@jit(nopython = True, cache = True)
def test_method():
    return numpy.dot(test_array, test_vector)


def test_method2(test_vector):
    test_vector[0], test_vector[1] = test_vector[1], test_vector[0]
    return test_vector


@jit(nopython = True)
def test_method3(test_vector, test_array):
    return numpy.dot(test_array, test_vector)


def test_method4():
    test_vector[0], test_vector[1] = test_vector[1], test_vector[0]
    return test_vector


if __name__ == '__main__':
    test_method()
    test_method2(test_vector)
    test_method3(test_vector, test_array)
    test_method4()
    loop_count = 10000
    total_time = 0
    total_time2 = 0
    total_time3 = 0
    total_time4 = 0
    for i in range(loop_count):
        start = time.time()
        test_method()
        total_time += time.time() - start
        start2 = time.time()
        test_method2(test_vector)
        total_time2 += time.time() - start2
        start3 = time.time()
        test_method3(test_vector, test_array)
        total_time3 += time.time() - start3
        start4 = time.time()
        test_method4()
        total_time4 += time.time() - start4
    print(total_time / loop_count)
    print(total_time2 / loop_count)
    print(total_time3 / loop_count)
    print(total_time4 / loop_count)
    dis.dis(test_method)
    dis.dis(test_method2)
    dis.dis(test_method3)
    dis.dis(test_method4)
