from general.table import IterableTable, TablePosition


def test_table_position():
    y = IterableTable(3, [[[], [], [1]], [[], [2]], [[1]]], 0)
    assert not y.has_any(TablePosition([0, 2, 1]), 2)
    assert y.has_any(TablePosition([0, 2, 1]), 1)
    assert not y.has_any(TablePosition([0, 3, 0]), 2)
    assert not y.has_any(TablePosition([0, 3, 0]), 1)
    assert y.has_any(TablePosition([0, 3, 0]), 0)
    assert not y.has_any(TablePosition([1, 0, 0]), 2)
    assert y.has_any(TablePosition([1, 0, 0]), 1)
    assert y.has_any(TablePosition([1, 1, 0]), 2)
    assert y.has(TablePosition([1, 1, 0]))
    assert TablePosition([0, 2, 0]).next(y.has, y.has_any) \
        == TablePosition([1, 1, 0])
