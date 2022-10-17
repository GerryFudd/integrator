from unittest import TestCase

from algebra.linear import LinearSystem, AffineSubspace, \
    InconsistentLinearSystem, Point, LinearSubspace
from custom_numbers.exact.rational_number import RationalNumber
from custom_numbers.radicals.reciprocals import p_square


def test_solves_system():
    linear_system = LinearSystem.of(['x', 'y'], [[1, 2, 3], [0, 2, 4]])
    assert linear_system.solve() == AffineSubspace(
        ['x', 'y'],
        Point({'x': -1, 'y': 2}),
        LinearSubspace(['x', 'y'], [[], []])
    )


def test_solves_system_with_rows_reversed():
    linear_system = LinearSystem.of(['x', 'y'], [[0, 2, 4], [1, 2, 3]])
    assert linear_system.solve() == AffineSubspace(
        ['x', 'y'],
        Point({'x': -1, 'y': 2}),
        LinearSubspace(['x', 'y'], [[], []])
    )


def test_solves_system_with_indeterminate_variables():
    linear_system = LinearSystem.of(
        ['x', 'y', 'z'],
        [
            [3, -4, 2, 8],
            [2, 0, 6, 3]
        ]
    )
    # [6, -8, 4, 16],
    # [6, 0, 18, 9]

    # [1, -4/3, 2/3, 8/3]
    # [0, 8/3, 14/3, -7/3]
    # [6, -8, 4, 16],
    # [0, 8, 14, -7]

    # [6, 0, 18, 9]
    # [0, 8, 14, -7]

    # [1, 0, 3, 1.5]
    # [0, 1, 1.75, -0.875]
    assert linear_system.solve() == AffineSubspace(
        ['x', 'y', 'z'],
        Point({'x': RationalNumber(3, 2), 'y': RationalNumber(-7, 8)}),
        LinearSubspace(['x', 'y'], [[-3], [RationalNumber(-7, 4)]]),
    )


def test_provides_rational_solutions():
    assert LinearSystem.of(['x'], [[3, 1]]).solve() == AffineSubspace(
        ['x'], Point({'x': RationalNumber(1, 3)}), LinearSubspace(['x'], [[]])
    )


def test_solves_power_square():
    assert p_square(2) == AffineSubspace.pure_subspace(
        ['z'], LinearSubspace(['a[0,1]', 'a[1,0]', 'a[1,1]'], [[-1], [-1], [2]])
    )

    assert p_square(3) == AffineSubspace.pure_subspace(
        ['z'],
        LinearSubspace(
            ['a[0,1]', 'a[0,2]',
             'a[1,0]', 'a[1,1]', 'a[1,2]',
             'a[2,0]', 'a[2,1]', 'a[2,2]'],
            [
                [-1], [1],
                [-1], [2], [-3],
                [1], [-3], [6]
            ]
        )
    )

    assert p_square(4) == AffineSubspace.pure_subspace(
        ['z'],
        LinearSubspace(
            ['a[0,1]', 'a[0,2]', 'a[0,3]',
             'a[1,0]', 'a[1,1]', 'a[1,2]', 'a[1,3]',
             'a[2,0]', 'a[2,1]', 'a[2,2]', 'a[2,3]',
             'a[3,0]', 'a[3,1]', 'a[3,2]', 'a[3,3]'],
            [
                [-1], [1], [-1],
                [-1], [2], [-3], [4],
                [1], [-3], [6], [-10],
                [-1], [4], [-10], [20],
            ]
        )
    )


def test_solves_power_square_with_top():
    assert p_square(2, top_vals=AffineSubspace.pure_subspace(
        ['1'], LinearSubspace(['a[1,1]'], [[2]])
    )) == AffineSubspace.pure_subspace(
        ['y[1]', 'z'],
        LinearSubspace(
            ['a[0,1]', 'a[1,0]', 'a[1,1]'],
            [
                [-2, -1],
                [0, -1], [2, 2],
            ]
        )
    )

    assert p_square(3, top_vals=AffineSubspace.pure_subspace(
        ['1'], LinearSubspace(['a[2,1]', 'a[2,2]'], [[-3], [6]])
    )) == AffineSubspace.pure_subspace(
        ['y[1]', 'z'],
        LinearSubspace(
            ['a[0,1]', 'a[0,2]',
             'a[1,0]', 'a[1,1]', 'a[1,2]',
             'a[2,0]', 'a[2,1]', 'a[2,2]'],
            [
                [3, -1], [-9, 1],
                [0, -1], [-3, 2], [12, -3],
                [0, 1], [3, -3], [-15, 6]
            ]
        )
    )

    assert p_square(4, top_vals=AffineSubspace.pure_subspace(
        ['1'], LinearSubspace(
            ['a[3,1]', 'a[3,2]', 'a[3,3]'],
            [[4], [-10], [20]]
        )
    )) == AffineSubspace.pure_subspace(
        ['y[1]', 'z'],
        LinearSubspace(
            ['a[0,1]', 'a[0,2]', 'a[0,3]',
             'a[1,0]', 'a[1,1]', 'a[1,2]', 'a[1,3]',
             'a[2,0]', 'a[2,1]', 'a[2,2]', 'a[2,3]',
             'a[3,0]', 'a[3,1]', 'a[3,2]', 'a[3,3]'],
            [
                [-4, -1], [14, 1], [-34, -1],
                [0, -1], [4, 2], [-18, -3], [52, 4],
                [0, 1], [-4, -3], [22, 6], [-74, -10],
                [0, -1], [4, 4], [-26, -10], [100, 20]
            ]
        )
    )

    # assert p_square(4) == AffineSubspace.exact(Point({
    #     'a[0,0]': 1, 'a[0,1]': -1, 'a[0,2]': 1, 'a[0,3]': -1,
    #     'a[1,0]': -1, 'a[1,1]': 2, 'a[1,2]': -3, 'a[1,3]': 4,
    #     'a[2,0]': 1, 'a[2,1]': -3, 'a[2,2]': 6, 'a[2,3]': -10,
    #     'a[3,0]': -1, 'a[3,1]': 4, 'a[3,2]': -10, 'a[3,3]': 20,
    # }))


class TestLinearSystem(TestCase):
    def test_raises_error_when_inconsistent(self):
        linear_system = LinearSystem.of(['x', 'y'], [[2, 4, 4], [1, 2, 3]])
        with self.assertRaises(InconsistentLinearSystem):
            linear_system.solve()
