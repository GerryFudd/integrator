import time
from decimal import Decimal
from math import pi
from unittest import TestCase

from calculus.integrator import Integrator, Mode


class TestIntegratorPerformance(TestCase):
    def test_calculate_circle_area_to_precision_timing(self):
        integrator = Integrator(lambda x: 4 * (1 - x ** 2) ** Decimal('0.5'),
                                Mode.DECREASING)
        duration = 0
        precision = 0
        while duration < 1000 and precision <= 8:
            previous_duration = duration
            precision = precision + 1
            start = time.thread_time_ns()
            value, error = integrator.integral_to_precision(0, 1, precision, 2)
            assert value == Decimal(str(round(pi, precision)))
            assert round(value + error, precision) == value
            assert round(value - error, precision) == value
            duration = (time.thread_time_ns() - start) // 1000000
            print(f'Completed trial for precision {precision} in '
                  f'{duration} ms.')
            if previous_duration > 0:
                print(f'This represents growth by a factor of '
                      f'{round(duration / previous_duration, 1)}')
        assert precision >= 6

    def test_calculate_elliptic_integrals(self):
        def error_function(a, error):
            return (
                       1 + a * error
                       - (1 + 2 * a * error - error ** 2) ** Decimal('0.5')
                   ) / (a ** 2 + 1)

        # This is the function that is integrated from 0 to t to evaluate
        # 2 * a * EllipticE(t, k)
        # where k = 1 - 1 / a^2
        def elliptic_function(a, x):
            return 2 * (
                (a ** 2 + (1 - a ** 2) * x ** 2) / (1 - x ** 2)
            ) ** Decimal('0.5')

        def get_elliptic_integrator(a):
            return Integrator(
                lambda x: elliptic_function(a, x),
                Mode.DECREASING
            )
        elliptic_integrator_doubled = get_elliptic_integrator(2)
        assert elliptic_integrator_doubled.integral_to_precision(
            0, 1, precision=3, resolution=2,
            error_func_upper=lambda e: error_function(2, e)
        )[0] == Decimal('4.844')
        # The true value of 2 * 2 * EllipticE(1 - 1 / 2^2) is
        # 4.8442241102738380992142515981959147059769591989433004125415581762
