from algebra.linear.powers import PSquareSide, p_square, \
    PSquareSeed, Direction, solve_full_system
from algebra.linear.subspace import Point


def test_new_p_square():
    result = p_square(PSquareSeed(
        4, left_seed=PSquareSide.zero(4, Direction.right()), top_seed=PSquareSide.zero(4, Direction.down()),
        start_vals={(0, 0): 1}))
    assert result.get_values() == [
        [1, -1, 1, -1],
        [-1, 2, -3, 4],
        [1, -3, 6, -10],
        [-1, 4, -10, 20]
    ]

    # [-1, 4, -10, 20]
    for mapping in [
        ({(0, 3): 1},  -1),
        ({(1, 3): 1},   4),
        ({(2, 3): 1}, -10),
        ({(3, 3): 1},  20),
    ]:
        assert mapping in result.right.mappings

    # [-1, 4, -10, 20]
    for mapping in [
        ({(3, 0): 1},  -1),
        ({(3, 1): 1},   4),
        ({(3, 2): 1}, -10),
        ({(3, 3): 1},  20),
    ]:
        assert mapping in result.bottom.mappings


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
    check_solution(solve_full_system(4), 4)


def test_with_five():
    check_solution(solve_full_system(5), 5)
