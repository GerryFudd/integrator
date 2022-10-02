from __future__ import annotations
from abc import abstractmethod
from typing import Protocol


class Numeric(Protocol):
    @abstractmethod
    def __add__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __mul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __sub__(self, other):
        raise NotImplementedError


def minimum(a, b):
    if a <= b:
        return a
    return b


def maximum(a, b):
    if a >= b:
        return a
    return b


def vector_sum(l1, l2):
    result = []
    for i in range(maximum(len(l1), len(l2))):
        if len(l1) <= i:
            result.append(l2[i])
        elif len(l2) <= i:
            result.append(l1[i])
        else:
            result.append(l1[i] + l2[i])
    return result
