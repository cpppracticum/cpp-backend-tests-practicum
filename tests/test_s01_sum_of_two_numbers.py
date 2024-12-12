from hypothesis import given
from hypothesis.strategies import integers
from subprocess import Popen, PIPE


# TODO: поменять на правильный вызов бинаря
def sum_two_int64(x, y):
    p = Popen(['python3', 'main.py'], stdout=PIPE, stdin=PIPE)
    stdout, stderr = p.communicate(input=f'{x} {y}\n'.encode())
    return int(stdout.strip())


BOUND = 2**16


@given(integers(min_value=-BOUND, max_value=BOUND-1), integers(min_value=-BOUND, max_value=BOUND-1))
def test_sum(x, y):
    assert x + y == sum_two_int64(x, y)
