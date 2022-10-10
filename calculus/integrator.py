from enum import Enum
from typing import Callable

from custom_numbers.types import ComputationType
from custom_numbers.exact import ExactNumber
from custom_numbers.utils import minimum, maximum
from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.simple import CharacteristicFunction, Interval, \
    SimpleFunction
from elementary_functions.utils import FunctionSum


class Mode(Enum):
    FLUCTUATING = 0
    INCREASING = 1
    DECREASING = 2


class IntegrationResult:
    def __init__(self, min, max, trap) -> None:
        self.min = min
        self.max = max
        self.trap = trap


class Integrator:
    def __init__(
        self,
        zero_val: ComputationType,
        func: Callable[[ComputationType], ComputationType],
        mode=Mode.FLUCTUATING
    ) -> None:
        self.zero_val = zero_val
        self.func = func
        self.cache = {}
        self.mode = mode

    def cached_func(self, x):
        if x not in self.cache:
            self.cache[x] = self.func(x)
        return self.cache[x]

    def __reset_cache(self):
        self.cache = {}

    def __get_out_range(self, a, b):
        if self.mode == Mode.FLUCTUATING:
            return output_range(self.cached_func, a, b)
        elif self.mode == Mode.INCREASING:
            return list(map(self.cached_func, [a, b]))
        elif self.mode == Mode.DECREASING:
            return list(map(self.cached_func, [b, a]))
        else:
            raise Exception(f'Mode {str(self.mode)} is not supported.')

    def __get_range_values(self, a, b):
        ran = self.__get_out_range(a, b)
        return ((b - a) * (self.cached_func(a) + self.cached_func(b)) / 2,
                (b - a) * ran[0],
                (b - a) * ran[1])

    def integrate(self, a, b, n):
        self.__reset_cache()
        min_y = self.zero_val
        max_y = self.zero_val
        trap = self.zero_val
        d = (self.zero_val + b - a) / n
        for p in range(0, n):
            values = self.__get_range_values(
                a + p * d,
                a + (p + 1) * d
            )
            trap = trap + values[0]
            min_y = min_y + values[1]
            max_y = max_y + values[2]
        self.__reset_cache()
        return IntegrationResult(min_y, max_y, trap)

    def difference_func(self, a, b):
        return lambda x: self.cached_func(x) - (
            (self.cached_func(b) - self.cached_func(a)) * (x - a) / (b - a)
            + self.cached_func(a)
        )

    def __get_difference_extrema(self, a, b, resolution=100):
        return get_local_extrema(self.difference_func(a, b), a, b, resolution)

    def __get_max_error_for_interval(self, a, b, resolution=100):
        ran = output_range(self.difference_func(a, b), a, b, resolution)
        return (b - a) * (ran[1] - ran[0])

    def integral_to_precision(
        self, a, b, precision, resolution=4,
        error_func_lower=lambda x: 0, error_func_upper=lambda x: 0
    ):
        self.__reset_cache()
        if resolution < 2:
            raise Exception('Resolution may not be smaller than 2. A resolution'
                            ' of 1 will never identify any error in the results'
                            ' because this will only evaluate the function at'
                            ' its endpoints.')
        tolerance = (self.zero_val + 10) ** (-precision - 1) / 2
        allowed_error = tolerance / 10
        initial_candidate = [
            self.zero_val + a + error_func_lower(allowed_error),
            self.zero_val + b - error_func_upper(allowed_error),
        ]
        candidates = [initial_candidate]
        errors = [self.__get_max_error_for_interval(
            initial_candidate[0], initial_candidate[1], resolution
        )]
        sample = []
        total_error = 0
        if initial_candidate[0] > a:
            total_error = total_error + allowed_error
        if initial_candidate[1] < b:
            total_error = total_error + allowed_error

        while sum(errors) + total_error >= tolerance:
            new_candidates = []
            new_errors = []
            for n in range(len(candidates)):
                if (candidates[n][1] - candidates[n][0]) * tolerance \
                        > (b - a) * errors[n]:
                    sample.append(candidates[n])
                    total_error = total_error + errors[n]
                else:
                    extrema_for_interval = self.__get_difference_extrema(
                        candidates[n][0], candidates[n][1], resolution
                    )
                    for m in range(1, len(extrema_for_interval)):
                        candidate = [
                            extrema_for_interval[m - 1], extrema_for_interval[m]
                        ]
                        new_candidates.append(candidate)
                        new_errors.append(self.__get_max_error_for_interval(
                            candidate[0], candidate[1], resolution
                        ))
            candidates = new_candidates
            errors = new_errors

        sample.extend(candidates)
        total_error = total_error + sum(errors)
        integral = 0
        for interval in sample:
            integral = integral + (interval[1] - interval[0]) * (
                self.cached_func(interval[0]) + self.cached_func(interval[1])
            ) / 2
        self.__reset_cache()
        return round(integral, precision), total_error


def integrate_exact(func, a, b):
    exact_a = ExactNumber.of(a)
    exact_b = ExactNumber.of(b)
    if isinstance(func, PowerFunction):
        new_power = func.power + 1
        anti_derivative = PowerFunction(
            new_power,
            ExactNumber.of(func.coefficient) / new_power
        )
        return anti_derivative.evaluate(exact_b) \
            - anti_derivative.evaluate(exact_a)
    if isinstance(func, FunctionSum) \
            or isinstance(func, Polynomial) \
            or isinstance(func, SimpleFunction):
        return sum(map(
            lambda x: integrate_exact(x, exact_a, exact_b),
            func.constituents
        ))
    if isinstance(func, CharacteristicFunction):
        if not func.domain.intersects(Interval(exact_a, exact_b)):
            return 0
        return func.coefficient * (
            func.domain * Interval(exact_a, exact_b)
        ).measure()

    raise NotImplementedError


def output_range(func, lower, upper, resolution=100):
    # Capture the outputs at the lower and upper endpoints
    lower_val = func(lower)
    upper_val = func(upper)

    # These are the minimum and maximum outputs on this interval.
    # They are initialized as the minimum and maximum from the ends of the
    # interval. These values are corrected as values from the middle are
    # sampled.
    abs_minimum = minimum(lower_val, upper_val)
    abs_maximum = maximum(lower_val, upper_val)
    for n in range(1, resolution):
        # This is the current sampled value. It will increase linearly
        # from lower_decimal to upper_decimal. The actual lower_decimal
        # and upper_decimal values are not re-sampled because they were already
        # captured.
        x = lower + (upper - lower) * n / resolution
        val = func(x)
        abs_minimum = minimum(abs_minimum, val)
        abs_maximum = maximum(abs_maximum, val)
    return abs_minimum, abs_maximum


def get_local_extrema(func, a, b, resolution=100):
    last_direction = 0
    last_x = a
    last_val = func(last_x)
    local_extrema = []
    for n in range(1, resolution + 1):
        x = a + (b - a) * n / resolution
        val = func(x)
        direction = val - last_val

        if last_direction <= 0 < direction:
            local_extrema.append(last_x)
        if direction < 0 <= last_direction:
            local_extrema.append(last_x)
        last_x = x
        last_val = val
        last_direction = direction
    local_extrema.append(b)
    return local_extrema
