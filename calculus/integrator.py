import time
from decimal import Decimal
from enum import Enum

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
    def __init__(self, func, mode=Mode.FLUCTUATING) -> None:
        self.cache = {}

        def cached_func(x):
            if x not in self.cache:
                self.cache[x] = func(x)
            return self.cache[x]

        self.cached_func = cached_func
        self.mode = mode

    def __reset_cache(self):
        print(f'Resetting cache. Previous cache size: {len(self.cache)}')
        self.cache = {}

    def __get_out_range(self, a, b):
        if self.mode == Mode.FLUCTUATING:
            return output_range(self.cached_func, a, b)
        elif self.mode == Mode.INCREASING:
            return *list(map(self.cached_func, [a, b])), [a], [b]
        elif self.mode == Mode.DECREASING:
            return *list(map(self.cached_func, [b, a])), [b], [a]
        else:
            raise Exception(f'Mode {str(self.mode)} is not supported.')

    def __get_range_values(self, a, b):
        ran = self.__get_out_range(a, b)
        return ((b - a) * (self.cached_func(a) + self.cached_func(b)) / 2,
                (b - a) * ran[0],
                (b - a) * ran[1])

    def integrate(self, a, b, n):
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

    def integral_to_precision(self, a, b, precision, resolution=4):
        if resolution < 2:
            raise Exception('Resolution may not be smaller than 2. A resolution'
                            ' of 1 will never identify any error in the results'
                            ' because this will only evaluate the function at'
                            ' its endpoints.')
        start = time.thread_time_ns()
        tolerance = Decimal('0.1') ** (precision + 1) / 2
        candidates = [[a, b]]
        errors = [self.__get_max_error_for_interval(a, b, resolution)]
        sample = []
        total_error = 0
        while sum(errors) + total_error >= tolerance:
            new_candidates = []
            new_errors = []
            largest_error = None
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
        ns_per_cache = (time.thread_time_ns() - start) / len(self.cache)
        print(
            f'The time per cached value is '
            f'{round(Decimal(ns_per_cache / 1000000), 3)}'
            f' ms per evaluation.'
        )
        print(
            f'The number of cached values per sample value is '
            f'{round(len(self.cache) / (len(sample) + 1), 2)}'
        )
        self.__reset_cache()
        return integral, total_error
