from unittest import TestCase

from algebra.linear import LinearSystem, AffineSubspace, \
    InconsistentLinearSystem, Point, LinearSubspace
from custom_numbers.exact.rational_number import RationalNumber


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
    assert linear_system.solve() == AffineSubspace(
        ['x', 'y', 'z'],
        Point({'x': RationalNumber(3, 2), 'y': RationalNumber(-7, 8)}),
        LinearSubspace(['x', 'y'], [[-3], [RationalNumber(-7, 4)]]),
    )


def test_provides_rational_solutions():
    assert LinearSystem.of(['x'], [[3, 1]]).solve() == AffineSubspace(
        ['x'], Point({'x': RationalNumber(1, 3)}), LinearSubspace(['x'], [[]])
    )


class TestLinearSystem(TestCase):
    def test_raises_error_when_inconsistent(self):
        linear_system = LinearSystem.of(['x', 'y'], [[2, 4, 4], [1, 2, 3]])
        with self.assertRaises(InconsistentLinearSystem):
            linear_system.solve()
