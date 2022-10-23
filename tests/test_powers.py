from algebra.linear.powers import solve_full_system
from algebra.linear.subspace import Point
from algebra.linear.utils import TimingContext


def check_solution(result: Point, p: int):
    for x, y in result.variable_list:
        if x + y >= p**2:
            assert result[(x, y)] == 0
        if x % p != 0 or y % p != 0:
            summation = 0
            if x > 0:
                summation += result[(x-1, y)]
            if y > 0:
                summation += result[(x, y-1)]
            summation += result[(x, y)]
            assert summation == 0


def test_new_solve_full_system():
    with TimingContext.get() as timing:
        result = solve_full_system(4)
    check_solution(result, 4)
    print(timing.get_results())


def test_with_five():
    with TimingContext.get() as timing:
        result = solve_full_system(5)
    check_solution(result, 5)
    print(timing.get_results())
