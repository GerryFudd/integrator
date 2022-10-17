from algebra.linear import AffineSubspace, LinearSubspace
from algebra.powers import p_square


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


def test_solves_power_square_with_left():
    assert p_square(2, AffineSubspace.pure_subspace(
        ['1'], LinearSubspace(['a[1,1]'], [[2]])
    )) == AffineSubspace.pure_subspace(
        ['y[1]', 'z'],
        LinearSubspace(
            ['a[0,1]', 'a[1,0]', 'a[1,1]'],
            [
                [0, -1],
                [-2, -1], [2, 2],
            ]
        )
    )

    assert p_square(3, AffineSubspace.pure_subspace(
        ['1'], LinearSubspace(['a[1,2]', 'a[2,2]'], [[-3], [6]])
    )) == AffineSubspace.pure_subspace(
        ['y[1]', 'z'],
        LinearSubspace(
            ['a[0,1]', 'a[0,2]',
             'a[1,0]', 'a[1,1]', 'a[1,2]',
             'a[2,0]', 'a[2,1]', 'a[2,2]'],
            [
                [0, -1], [0, 1],
                [3, -1], [-3, 2], [3, -3],
                [-9, 1], [12, -3], [-15, 6]
            ]
        )
    )

    assert p_square(4, AffineSubspace.pure_subspace(
        ['1'], LinearSubspace(
            ['a[1,3]', 'a[2,3]', 'a[3,3]'],
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
                [0, -1], [0, 1], [0, -1],
                [-4, -1], [4, 2], [-4, -3], [4, 4],
                [14, 1], [-18, -3], [22, 6], [-26, -10],
                [-34, -1], [52, 4], [-74, -10], [100, 20]
            ]
        )
    )


def test_solves_power_square_with_top_and_left():
    assert p_square(
        2,
        AffineSubspace.pure_subspace(
            ['1', '2'], LinearSubspace(['a[1,1]'], [[2, 2]])
        ),
        AffineSubspace.pure_subspace(
            ['1', '2'], LinearSubspace(['a[1,1]'], [[2, 2]])
        )
    ) == AffineSubspace.pure_subspace(
        ['y[1]', 'y[2]', 'z'],
        LinearSubspace(
            ['a[0,1]', 'a[1,0]', 'a[1,1]'],
            [
                [-2, -2, -1],
                [-2, -2, -1], [4, 4, 2],
            ]
        )
    )

    assert p_square(
        4,
        AffineSubspace.pure_subspace(
            ['1', '2'], LinearSubspace(
                ['a[1,3]', 'a[2,3]', 'a[3,3]'],
                [[52, 4], [-74, -10], [100, 20]],
            )
        ),
        AffineSubspace.pure_subspace(
            ['1', '2'], LinearSubspace(
                ['a[3,1]', 'a[3,2]', 'a[3,3]'],
                [[52, 4], [-74, -10], [100, 20]],
            )
        )
    ) == AffineSubspace.pure_subspace(
        ['y[1]', 'y[2]', 'z'],
        LinearSubspace(
            ['a[0,1]', 'a[0,2]', 'a[0,3]',
             'a[1,0]', 'a[1,1]', 'a[1,2]', 'a[1,3]',
             'a[2,0]', 'a[2,1]', 'a[2,2]', 'a[2,3]',
             'a[3,0]', 'a[3,1]', 'a[3,2]', 'a[3,3]'],
            [
                [-52, -4, -1], [126, 14, 1], [-226, -34, -1],
                [-52, -4, -1], [104, 8, 2], [-230, -22, -3], [456, 56, 4],
                [126, 14, 1], [-230, -22, -3], [460, 44, 6], [-916, -100, -10],
                [-226, -34, -1], [456, 56, 4], [-916, -100, -10],
                [1832, 200, 20]
            ]
        )
    )
