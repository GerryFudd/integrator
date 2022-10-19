from unittest import TestCase

from algebra.linear.subspace import AffineSubspace, Point, \
    LinearSystem, InconsistentLinearSystem
from custom_numbers.exact.rational_number import RationalNumber


def test_solves_system():
    linear_system = LinearSystem.of(['x', 'y'], [[1, 2, 3], [0, 2, 4]])
    assert linear_system.solve() == AffineSubspace.exact(Point.builder().map('x', -1).map('y', 2).build())


def test_solves_system_with_rows_reversed():
    linear_system = LinearSystem.of(['x', 'y'], [[0, 2, 4], [1, 2, 3]])
    assert linear_system.solve() == AffineSubspace.exact(Point.builder().map('x', -1).map('y', 2).build())


def test_solves_system_with_indeterminate_variables():
    linear_system = LinearSystem.of(
        ['x', 'y', 'z'],
        [
            [3, -4, 2, 8],
            [2, 0, 6, 3]
        ]
    )
    assert linear_system.solve() == AffineSubspace(LinearSystem.of(
        ['x', 'y', 'z'],
        [
            [1, 0, 3, 1.5],
            [0, 1, 1.75, -0.875]
        ]
    ))


def test_provides_rational_solutions():
    assert LinearSystem.of(['x'], [[3, 1]]).solve() == AffineSubspace.exact(
        Point.builder().map('x', RationalNumber(1, 3)).build()
    )


class TestLinearSystem(TestCase):
    def test_raises_error_when_inconsistent(self):
        linear_system = LinearSystem.of(
            ['x', 'y'], [[2, 4, 4], [1, 2, 3]]
        )
        with self.assertRaises(InconsistentLinearSystem):
            linear_system.solve()
