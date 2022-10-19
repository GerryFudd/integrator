from algebra.linear.equations import MultiDimensionalEquation
from algebra.linear.powers import p_square, solve_left_side
from algebra.linear.subspace import AffineSubspace, Point, LinearSystem
from custom_numbers.types import Numeric


def test_solves_power_square():
    assert p_square(4, seed=AffineSubspace.exact(Point.builder().map('a[0,0]', 1).build()).linear_system.equations) \
           == AffineSubspace.exact(
        Point.builder()
        .map('a[0,0]', 1)
        .map('a[0,0]', 1)
        .map('a[0,1]', -1)
        .map('a[0,2]', 1)
        .map('a[0,3]', -1)
        .map('a[1,0]', -1)
        .map('a[1,1]', 2)
        .map('a[1,2]', -3)
        .map('a[1,3]', 4)
        .map('a[2,0]', 1)
        .map('a[2,1]', -3)
        .map('a[2,2]', 6)
        .map('a[2,3]', -10)
        .map('a[3,0]', -1)
        .map('a[3,1]', 4)
        .map('a[3,2]', -10)
        .map('a[3,3]', 20)
        .build()
    )


def m_out_of_n(m: int, n: int):
    return [0] * m + [1] + [0] * (n - m - 1)


def map_to_position(tails: list[list[Numeric]]):
    return list(map(
        lambda x: m_out_of_n(x[0], len(tails)) + x[1],
        enumerate(tails)
    ))


def test_solves_power_square_with_top():
    assert p_square(4, seed=[
        MultiDimensionalEquation({'a[3,1]': 1, 'a[0,0]': -4}, 0, ['a[3,1]', 'a[3,2]', 'a[3,3]', 'a[0,0]']),
        MultiDimensionalEquation({'a[3,2]': 1, 'a[0,0]': 10}, 0, ['a[3,1]', 'a[3,2]', 'a[3,3]', 'a[0,0]']),
        MultiDimensionalEquation({'a[3,3]': 1, 'a[0,0]': -20}, 0, ['a[3,1]', 'a[3,2]', 'a[3,3]', 'a[0,0]']),
    ],
        top_vars=['a[3,1]', 'a[3,2]', 'a[3,3]'],
        symbol='b') == AffineSubspace(
            LinearSystem.of(
                [
                    'a[3,1]', 'a[3,2]', 'a[3,3]',
                    'b[0,1]', 'b[0,2]', 'b[0,3]',
                    'b[1,0]', 'b[1,1]', 'b[1,2]', 'b[1,3]',
                    'b[2,0]', 'b[2,1]', 'b[2,2]', 'b[2,3]',
                    'b[3,0]', 'b[3,1]', 'b[3,2]', 'b[3,3]',
                    'b[0,0]', 'a[0,0]'],
                map_to_position(
                    [
                        [0, -4, 0],
                        [0, 10, 0],
                        [0, -20, 0],
                        [1, 4, 0],
                        [-1, -14, 0],
                        [1, 34, 0],
                        [1, 0, 0],
                        [-2, -4, 0],
                        [3, 18, 0],
                        [-4, -52, 0],
                        [-1, 0, 0],
                        [3, 4, 0],
                        [-6, -22, 0],
                        [10, 74, 0],
                        [1, 0, 0],
                        [-4, -4, 0],
                        [10, 26, 0],
                        [-20, -100, 0],
                    ]
                )
            )
    )


def test_solves_power_square_with_left():
    assert p_square(
        4,
        seed=[
            MultiDimensionalEquation({'a[1,3]': 1, 'a[0,0]': -4}, 0, ['a[1,3]', 'a[2,3]', 'a[3,3]', 'a[0,0]']),
            MultiDimensionalEquation({'a[2,3]': 1, 'a[0,0]': 10}, 0, ['a[1,3]', 'a[2,3]', 'a[3,3]', 'a[0,0]']),
            MultiDimensionalEquation({'a[3,3]': 1, 'a[0,0]': -20}, 0, ['a[1,3]', 'a[2,3]', 'a[3,3]', 'a[0,0]']),
        ],
        left_vars=['a[1,3]', 'a[2,3]', 'a[3,3]'], symbol='q') == AffineSubspace(
        LinearSystem.of(
            [
                'a[1,3]', 'a[2,3]', 'a[3,3]',
                'q[0,1]', 'q[0,2]', 'q[0,3]',
                'q[1,0]', 'q[1,1]', 'q[1,2]', 'q[1,3]',
                'q[2,0]', 'q[2,1]', 'q[2,2]', 'q[2,3]',
                'q[3,0]', 'q[3,1]', 'q[3,2]', 'q[3,3]',
                'q[0,0]', 'a[0,0]'
            ],
            map_to_position([
                [0, -4, 0],
                [0, 10, 0],
                [0, -20, 0],
                [1, 0, 0],
                [-1, 0, 0],
                [1, 0, 0],
                [1, 4, 0],
                [-2, -4, 0],
                [3, 4, 0],
                [-4, -4, 0],
                [-1, -14, 0],
                [3, 18, 0],
                [-6, -22, 0],
                [10, 26, 0],
                [1, 34, 0],
                [-4, -52, 0],
                [10, 74, 0],
                [-20, -100, 0],
            ])
        )
    )


def test_solves_power_square_with_top_and_left():
    assert p_square(
        4,
        symbol='g',
        seed=[
            MultiDimensionalEquation({'f[3,1]': 1, 'y': -52, 'z': -4}, 0, ['f[3,1]', 'f[3,2]', 'f[3,3]', 'y', 'z']),
            MultiDimensionalEquation({'f[3,2]': 1, 'y': 74, 'z': 10}, 0, ['f[3,1]', 'f[3,2]', 'f[3,3]', 'y', 'z']),
            MultiDimensionalEquation({'f[3,3]': 1, 'y': -100, 'z': -20}, 0, ['f[3,1]', 'f[3,2]', 'f[3,3]', 'y', 'z']),
            MultiDimensionalEquation({'b[1,3]': 1, 'y': -52, 'z': -4}, 0, ['b[1,3]', 'b[2,3]', 'b[3,3]', 'y', 'z']),
            MultiDimensionalEquation({'b[2,3]': 1, 'y': 74, 'z': 10}, 0, ['b[1,3]', 'b[2,3]', 'b[3,3]', 'y', 'z']),
            MultiDimensionalEquation({'b[3,3]': 1, 'y': -100, 'z': -20}, 0, ['b[1,3]', 'b[2,3]', 'b[3,3]', 'y', 'z']),
        ],
        left_vars=['b[1,3]', 'b[2,3]', 'b[3,3]'],
        top_vars=['f[3,1]', 'f[3,2]', 'f[3,3]'],
    ) == AffineSubspace(LinearSystem.of(
        ['f[3,1]', 'f[3,2]', 'f[3,3]',
            'b[1,3]', 'b[2,3]', 'b[3,3]',
            'g[0,1]', 'g[0,2]', 'g[0,3]',
            'g[1,0]', 'g[1,1]', 'g[1,2]', 'g[1,3]',
            'g[2,0]', 'g[2,1]', 'g[2,2]', 'g[2,3]',
            'g[3,0]', 'g[3,1]', 'g[3,2]', 'g[3,3]',
            'g[0,0]', 'y', 'z'],
        map_to_position([
            [0, -52, -4, 0],
            [0, 74, 10, 0],
            [0, -100, -20, 0],
            [0, -52, -4, 0],
            [0, 74, 10, 0],
            [0, -100, -20, 0],
            [1, 52, 4, 0],
            [-1, -126, -14, 0],
            [1, 226, 34, 0],
            [1, 52, 4, 0],
            [-2, -104, -8, 0],
            [3, 230, 22, 0],
            [-4, -456, -56, 0],
            [-1, -126, -14, 0],
            [3, 230, 22, 0],
            [-6, -460, -44, 0],
            [10, 916, 100, 0],
            [1, 226, 34, 0],
            [-4, -456, -56, 0],
            [10, 916, 100, 0],
            [-20, -1832, -200, 0],
        ])
    ))


def test_find_iterated_squares():
    assert solve_left_side(3) == AffineSubspace(
        LinearSystem.of(
            ['a0[0,1]', 'a0[0,2]',
                'a0[1,0]', 'a0[1,1]', 'a0[1,2]',
                'a0[2,0]', 'a0[2,1]', 'a0[2,2]',
                'a1[0,1]', 'a1[0,2]',
                'a1[1,0]', 'a1[1,1]', 'a1[1,2]',
                'a1[2,0]', 'a1[2,1]', 'a1[2,2]',
                'a2[0,1]', 'a2[0,2]',
                'a2[1,0]', 'a2[1,1]', 'a2[1,2]',
                'a2[2,0]', 'a2[2,1]', 'a2[2,2]',
                'a2[0,0]', 'a1[0,0]',
                'a0[0,0]'],
            map_to_position([
                [1, 0],
                [-1, 0],
                [1, 0],
                [-2, 0],
                [3, 0],
                [-1, 0],
                [3, 0],
                [-6, 0],
                [-1, 0],
                [7, 0],
                [2, 0],
                [-1, 0],
                [-6, 0],
                [-2, 0],
                [3, 0],
                [3, 0],
                [-2, 0],
                [-1, 0],
                [1, 0],
                [1, 0],
                [-0, 0],
                [-1, 0],
                [-0, 0],
                [-0, 0],
                [-1, 0],
                [-2, 0],
            ])
        )
    )
