from decimal import Decimal

from advanced_functions.circle import Circle


def test_unit_circle():
    circ = Circle(0, 0, 1)
    for n in range(201):
        val = Decimal('0.01') * (n - 100)
        actual = circ.evaluate(val)
        print(f'actual: {actual}')
        expected = (1 - val ** 2) ** Decimal('0.5')
        print(f'expected: {expected}')
        assert actual == expected
