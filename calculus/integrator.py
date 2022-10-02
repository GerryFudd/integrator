from decimal import Decimal
from enum import Enum
from numbers import Number
from typing import Callable, Union
from types import FunctionType

from elementary_functions.polynomial import Polynomial
from elementary_functions.power_functions import PowerFunction
from elementary_functions.simple import CharacteristicFunction, Interval
from elementary_functions.utils import Function, WrappedFunction, FunctionScaled, \
    FunctionSum
from .utils import get_local_extrema, output_range


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
    def __init__(self, func: Union[Function, Callable[[Number], Number]],
                 mode=Mode.FLUCTUATING) -> \
            None:
        if isinstance(func, FunctionType):
            self.func = WrappedFunction(func)
        else:
            self.func = func

        self.cache = {}
        self.mode = mode

    def cached_func(self, x):
        if x not in self.cache:
            self.cache[x] = self.func.evaluate(x)
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
        min_y = Decimal('0')
        max_y = Decimal('0')
        trap = Decimal('0')
        d = (Decimal(str(b)) - Decimal(str(a))) / Decimal(str(n))
        for p in range(0, n):
            values = self.__get_range_values(a + p * d, a + (p + 1) * d)
            trap = trap + values[0]
            min_y = min_y + values[1]
            max_y = max_y + values[2]
        self.__reset_cache()
        return IntegrationResult(min_y, max_y, trap)

    def integrate_exact(self, a, b):
        if isinstance(self.func, PowerFunction):
            new_power = self.func.power + 1
            anti_derivative = FunctionScaled(
                1/new_power, PowerFunction(new_power)
            )
            return anti_derivative.evaluate(b) - anti_derivative.evaluate(a)
        if isinstance(self.func, FunctionScaled):
            return self.func.scale * Integrator(self.func.base_func)\
                .integrate_exact(a, b)
        if isinstance(self.func, FunctionSum) \
                or isinstance(self.func, Polynomial):
            return sum(map(
                lambda x: Integrator(x).integrate_exact(a, b),
                self.func.constituents
            ))
        if isinstance(self.func, CharacteristicFunction):
            return self.func.domain.intersect(Interval(a, b)).measure()

        raise NotImplementedError

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
        tolerance = Decimal('0.1') ** (precision + 1) / 2
        allowed_error = tolerance / 10
        initial_candidate = [
            a + error_func_lower(allowed_error),
            b - error_func_upper(allowed_error)
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
