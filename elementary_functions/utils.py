from abc import abstractmethod
from typing import Protocol, List, Callable
from general.numbers import Numeric


class Function(Protocol):
    @abstractmethod
    def evaluate(self, x: Numeric) -> Numeric:
        """A function must be able to take an input and render an output"""
        raise NotImplementedError

    @abstractmethod
    def __rmul__(self, other):
        """Allow functions to be scaled"""
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other):
        """Allow functions to be scaled"""
        raise NotImplementedError


class WrappedFunction:
    def __init__(self, f: Callable[[Numeric], Numeric]):
        self.f = f

    def evaluate(self, x: Numeric) -> Numeric:
        return self.f(x)

    def __rmul__(self, other):
        return WrappedFunction(lambda x: other * self.f(x))

    def __add__(self, other):
        return WrappedFunction(lambda x: self.f(x) + other.evaluate(x))


class FunctionSum:
    def __init__(self, *constituents):
        self.constituents: List[Function] = list(constituents)

    def __str__(self):
        return ' + '.join(map(str, self.constituents))

    def __repr__(self):
        return f'FunctionSum({",".join(map(str, self.constituents))})'

    def __eq__(self, other):
        if hasattr(other, 'constituents'):
            return set(self.constituents) == set(other.constituents)
        if len(self.constituents) == 0:
            return ConstantFunction() == other
        if len(self.constituents) > 1:
            return False
        return self.constituents[0] == other

    def evaluate(self, x: Numeric) -> Numeric:
        return sum(map(lambda f: f.evaluate(x), self.constituents))

    def __rmul__(self, other):
        return FunctionSum(*map(lambda f: other * f, self.constituents))

    def __add__(self, other):
        if isinstance(other, FunctionSum):
            return FunctionSum(*(self.constituents + other.constituents))
        return FunctionSum(*(self.constituents + [other]))


class ConstantFunction:
    def __init__(self, val: Numeric = 0):
        self.val = val

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return f'ConstantFunction({self.val})'

    def __eq__(self, other):
        return isinstance(other, ConstantFunction) and self.val == other.val

    def evaluate(self) -> Numeric:
        return self.val

    def __rmul__(self, other):
        return ConstantFunction(other * self.val)

    def __add__(self, other):
        if self.val == 0:
            return other
        return FunctionSum(self, other)
