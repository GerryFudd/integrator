import time
from decimal import Decimal
from math import pi
import unittest

from calculus.integrator import Integrator, Mode


class TestIntegrator(unittest.TestCase):
    def test_integrate_linear(self):
        result = Integrator(lambda x: 2 * x).integrate(0, 2, 4)
        assert result.trap == 4
        assert result.min == 3
        assert result.max == 5

    def test_integrate_linear_increasing(self):
        result = Integrator(lambda x: 2 * x, Mode.INCREASING).integrate(0, 2, 4)
        assert result.trap == 4
        assert result.min == 3
        assert result.max == 5

    def test_integrate_linear_decreasing(self):
        result = Integrator(lambda x: -2 * x, Mode.DECREASING)\
            .integrate(0, 2, 4)
        assert result.trap == -4
        assert result.min == -5
        assert result.max == -3

    def test_integrate_parabola(self):
        integrator = Integrator(lambda x: 3 * x ** 2)
        basic_result = integrator.integrate(-1, 1, 4)
        assert basic_result.trap == Decimal('2.25')
        assert basic_result.min == Decimal('0.75')
        assert basic_result.max == Decimal('3.75')

        messy_result = integrator.integrate(-1, 1, 5)
        assert messy_result.trap == Decimal('2.16')
        assert messy_result.min == Decimal('0.96')

    def test_calculate_circle_area(self):
        integrator = Integrator(lambda x: 4 * (1 - x ** 2) ** Decimal('0.5'),
                                Mode.DECREASING)
        first_approximation = integrator.integrate(0, 1, 10)
        assert round(first_approximation.trap, 1) == Decimal('3.1')
        assert first_approximation.max > first_approximation.min
        assert first_approximation.max - first_approximation.min < Decimal('0.5')

        second_approximation = integrator.integrate(0, 1, 100)
        assert round(second_approximation.trap, 2) == Decimal('3.14')
        assert second_approximation.max > second_approximation.min
        assert second_approximation.max - second_approximation.min \
               < Decimal('0.05')

    def test_calculate_circle_area_to_precision_one(self):
        integrator = Integrator(lambda x: 4 * (1 - x ** 2) ** Decimal('0.5'),
                                Mode.DECREASING)
        assert round(integrator.integral_to_precision(0, 1, 1, 2)[0], 1) \
               == Decimal('3.1')

    def test_calculate_circle_area_to_precision_five(self):
        integrator = Integrator(lambda x: 4 * (1 - x ** 2) ** Decimal('0.5'),
                                Mode.DECREASING)
        assert round(integrator.integral_to_precision(0, 1, 5, 2)[0], 5) == Decimal(
            '3.14159')

    def test_calculate_circle_area_to_precision_timing(self):
        integrator = Integrator(lambda x: 4 * (1 - x ** 2) ** Decimal('0.5'),
                                Mode.DECREASING)
        duration = 0
        precision = 0
        while duration < 1000 and precision <= 8:
            previous_duration = duration
            precision = precision + 1
            start = time.thread_time_ns()
            assert round(
                integrator.integral_to_precision(0, 1, precision, 2)[0],
                precision
            ) == Decimal(str(round(pi, precision)))
            duration = (time.thread_time_ns() - start) // 1000000
            print(f'Completed trial for precision {precision} in '
                  f'{duration} ms.')
            if previous_duration > 0:
                print(f'This represents growth by a factor of '
                      f'{round(duration / previous_duration, 1)}')
        assert precision >= 6
