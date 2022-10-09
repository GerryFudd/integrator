from advanced_functions.circle import Circle
from custom_numbers.computation import Number


def test_unit_circle():
    circ = Circle(0, 0, 1)
    for n in range(201):
        val = (Number.of(n) - 100) / 100
        actual = circ.evaluate(val)
        print(f'actual: {actual}')
        expected = (1 - val ** 2) ** 0.5
        print(f'expected: {expected}')
        assert actual == expected
