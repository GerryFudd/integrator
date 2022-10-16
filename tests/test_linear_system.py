from algebra.linear import LinearSystem, AffineSubspace, \
    MultiDimensionalEquation


def test_solves_system():
    linear_system = LinearSystem.of(['x', 'y'], [[1, 2, 3], [0, 2, 4]])
    assert linear_system.solve() == AffineSubspace(
        ['x', 'y'],
        MultiDimensionalEquation({'x': 1, 'y': 0}, -1),
        MultiDimensionalEquation({'x': 0, 'y': 1}, 2),
    )
