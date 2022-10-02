from __future__ import annotations

from typing import List, Tuple, Dict

from elementary_functions.utils import FunctionScaled, FunctionSum
from general.utils import maximum, minimum, Numeric


class Interval:
    def __init__(self, a: Numeric, b: Numeric):
        self.a = a
        self.b = b

    def __str__(self):
        return f'({self.a},{self.b})'

    def intersects(self, interval: Interval) -> bool:
        return self.a < interval.b and interval.a < self.b

    def contains(self, x: Numeric) -> bool:
        return self.a < x < self.b

    def intersect(self, other: Interval) -> Interval | None:
        if self.intersects(other):
            result = Interval(
                maximum(self.a, other.a),
                minimum(self.b, other.b),
            )
            return result

    def subtract(self, other: Interval) -> List[Interval]:
        result = []
        if self.a < other.a:
            result.append(Interval(self.a, other.a))
        if other.b < self.b:
            result.append(Interval(other.b, self.b))
        return result


class IntervalCollection:
    @staticmethod
    def from_intervals(*intervals: Tuple[Numeric, Numeric]):
        instance = IntervalCollection()
        for a, b in intervals:
            instance.add(Interval(a, b))
        return instance

    def __init__(self):
        self.intervals = []

    def __str__(self):
        return ','.join(map(str, self.intervals))

    def __iter__(self):
        return self.intervals.__iter__()

    def measure(self) -> Numeric:
        return sum(map(lambda x: x.b - x.a, self.intervals))

    def add(self, other: Interval) -> None:
        new_interval = other
        to_remove: List[Interval] = []
        for existing in self.intervals:
            if existing.intersects(other):
                new_interval = Interval(
                    minimum(existing.a, new_interval.a),
                    maximum(existing.b, new_interval.b),
                )
                to_remove.append(existing)
        for r in to_remove:
            self.intervals.remove(r)
        self.intervals.append(new_interval)

    def intersect(self, other: IntervalCollection | Interval):
        if isinstance(other, Interval):
            other_arg = IntervalCollection.from_intervals((other.a, other.b))
        else:
            other_arg = other
        new_intervals = IntervalCollection()
        for other_interval in other_arg:
            for this_interval in self.intervals:
                if this_interval.intersects(other_interval):
                    new_intervals.add(this_interval.intersect(other_interval))
        return new_intervals

    def contains(self, x: Numeric) -> bool:
        for interval in self.intervals:
            if interval.contains(x):
                return True
        return False


class CharacteristicFunction:
    @staticmethod
    def from_intervals(*intervals: Tuple[Numeric, Numeric]):
        return CharacteristicFunction(
            IntervalCollection.from_intervals(*intervals)
        )

    def __init__(self, domain: IntervalCollection):
        self.domain = domain

    def evaluate(self, x: Numeric) -> Numeric:
        if self.domain.contains(x):
            return 1
        return 0


class SimpleFunction:
    def __init__(self):
        self.linear_combo: Dict[Interval, Numeric] = {}

    def add(
        self,
        val: Numeric,
        *new_intervals: Tuple[Numeric, Numeric],
    ) -> SimpleFunction:
        for a, b in new_intervals:
            new_interval = Interval(a, b)
            to_remove = []
            to_add = {}
            for interval, r in self.linear_combo.items():
                if interval.intersects(new_interval):
                    to_add[new_interval.intersect(interval)] = val + r
                    for remainder in interval.subtract(new_interval):
                        to_add[remainder] = r
                    for remainder in new_interval.subtract(interval):
                        to_add[remainder] = val
                    to_remove.append(interval)
            if len(to_add) == 0:
                to_add[new_interval] = val
            for interval in to_remove:
                del self.linear_combo[interval]
            for interval, add_val in to_add.items():
                self.linear_combo[interval] = add_val
        return self

    @property
    def constituents(self):
        aggregated = {}
        for interval, val in self.linear_combo.items():
            if val not in aggregated:
                aggregated[val] = IntervalCollection()
            aggregated[val].add(interval)
        result = []
        for val, domain in aggregated.items():
            result.append(FunctionScaled(val, CharacteristicFunction(domain)))
        return result

    def evaluate(self, x: Numeric) -> Numeric:
        return FunctionSum(*self.constituents).evaluate(x)
