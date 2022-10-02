from __future__ import annotations

from numbers import Number
from typing import List


def min_num(a: Number, b: Number) -> Number:
    if a <= b:
        return a
    return b


def max_num(a: Number, b: Number) -> Number:
    if a >= b:
        return a
    return b


class Interval:
    def __int__(self, a: Number, b: Number):
        self.a = a
        self.b = b

    def intersects(self, interval: Interval) -> bool:
        return self.a < interval.b and interval.a < self.b

    def contains(self, x: Number) -> bool:
        return self.a < x < self.b


def intersect(int_a: Interval, int_b: Interval) -> Interval | None:
    if int_a.intersects(int_b):
        result = Interval(
            max_num(int_a.a, int_b.a),
            min_num(int_a.b, int_b.b),
        )
        return result


class IntervalCollection:
    @staticmethod
    def from_intervals(intervals):
        instance = IntervalCollection()
        for interval in intervals:
            instance.add(interval)
        return instance

    def __init__(self):
        self.intervals = []

    def __iter__(self):
        return self.intervals.__iter__()

    def add(self, other: Interval) -> None:
        new_interval = other
        to_remove: List[Interval] = []
        for existing in self.intervals:
            if existing.intersects(other):
                new_interval = Interval(
                    min_num(existing.a, new_interval.a),
                    max_num(existing.b, new_interval.b),
                )
                to_remove.append(existing)
        for r in to_remove:
            self.intervals.remove(r)
        self.intervals.append(new_interval)

    def intersect(self, other: IntervalCollection):
        new_intervals = IntervalCollection()
        for other_interval in other:
            for this_interval in self.intervals:
                if this_interval.intersects(other_interval):
                    new_intervals.add(intersect(this_interval, other_interval))
        return new_intervals

    def contains(self, x: Number) -> bool:
        for interval in self.intervals:
            if interval.contains(x):
                return True
        return False


class CharacteristicFunction:
    def __int__(self, domain: IntervalCollection):
        self.domain = domain

    def evaluate(self, x: Number) -> Number:
        if self.domain.contains(x):
            return 1
        return 0
