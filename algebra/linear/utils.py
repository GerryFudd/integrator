from __future__ import annotations

import time
from typing import Generic, Callable, TypeVar

from custom_numbers.types import Numeric

IterationValType = TypeVar('IterationValType')


class IndexedMapIterator(Generic[IterationValType]):
    def __init__(
        self, mapping: Callable[[str], IterationValType], key_index: list[str],
    ):
        self.mapping = mapping
        self.key_index = key_index
        self.current = -1

    def __next__(self) -> tuple[int, str, Numeric]:
        self.current += 1
        if self.current >= len(self.key_index):
            raise StopIteration
        key = self.key_index[self.current]
        return self.current, key, self.mapping(key)


class MissingTimingContextError(Exception):
    pass


class TimingMetricAmbiguityError(Exception):
    pass


class TimingResults:
    def __init__(self, name: str, duration_ms: int):
        self.name = name
        self.duration_ms = duration_ms
        self.children = []

    def append(self, value: TimingResults):
        self.children.append(value)

    def __str__(self):
        result = f'\n{self.name}: {self.duration_ms}ms'
        uncategorized = self.duration_ms
        for child in self.children:
            uncategorized -= child.duration_ms
            for line in str(child).split('\n'):
                if line:
                    result += f'\n\t{line}'
        if self.children:
            result += f'\n\tUncategorized: {uncategorized}ms'
        return result

    def __repr__(self):
        return f'TimingResults(name={self.name},duration_ms={self.duration_ms},children={self.children})'


class Profiler:
    def __init__(self, name: str):
        self.name = name
        self.metric = None

    def __enter__(self):
        if TimingContext.singleton is not None and self.name in TimingContext.singleton:
            self.metric = TimingContext.singleton[self.name]
        else:
            self.metric = TimingMetric(self.name)
        if TimingContext.singleton is not None:
            TimingContext.singleton.register(self.metric)
        self.metric.start = time.time()
        return self.metric

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.metric.stop()
        if TimingContext.singleton is not None:
            TimingContext.singleton.de_register(self.metric)
        if exc_type is not None:
            print(exc_val)


class TimingMetric:
    def __init__(self, name: str):
        self.name = name
        self.total_time = 0
        self.do_on_close = []
        self.do_get_child_result = []
        self.created = time.time()
        self.start = None

    def register(
        self, child_metric: TimingMetric,
    ):
        self.do_on_close.append(child_metric.stop)
        self.do_get_child_result.append(child_metric.get_results)

    def stop(self):
        if self.start is not None:
            self.total_time += time.time() - self.start
            self.start = None
        for on_close_callable in self.do_on_close:
            on_close_callable()

    def get_results(self) -> TimingResults:
        results = TimingResults(self.name, round(self.total_time * 1000))
        for get_child_result in self.do_get_child_result:
            results.append(get_child_result())
        return results

    def __eq__(self, other):
        return isinstance(other, TimingMetric) and self.name == other.name and self.created == other.created

    def __hash__(self):
        return hash((self.name, self.created, 'TimingMetric'))


class TimingContext:
    singleton: TimingContext = None

    @staticmethod
    def get():
        if TimingContext.singleton is None:
            TimingContext.singleton = TimingContext()
        return TimingContext.singleton

    def __init__(self):
        self.active: list[TimingMetric] = []
        self.registered: dict[str, TimingMetric] = {}

    def register(self, metric: TimingMetric):
        if metric.name in self:
            if metric != self[metric.name] or metric in self.active:
                raise TimingMetricAmbiguityError
        else:
            self.active[-1].register(metric)
            self[metric.name] = metric
        self.active.append(metric)

    def de_register(self, metric: TimingMetric):
        while metric in self.active:
            self.active.pop()

    def __contains__(self, item):
        return '-'.join(map(lambda x: x.name, self.active)) + f'-{item}' in self.registered

    def __getitem__(self, item):
        return self.registered['-'.join(map(lambda x: x.name, self.active)) + f'-{item}']

    def __setitem__(self, key, value):
        self.registered['-'.join(map(lambda x: x.name, self.active)) + f'-{key}'] = value

    def __enter__(self):
        self.metric = TimingMetric('Overall')
        self.metric.start = time.time()
        self.active.append(self.metric)
        return self.metric

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.metric.stop()
        TimingContext.singleton = None
        if exc_type is not None:
            print(exc_val)
