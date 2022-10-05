from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.simple import CharacteristicFunction
from elementary_functions.utils import Function, FunctionSum, WrappedFunction, \
    ConstantFunction


def differentiate(func: Function):
    if isinstance(func, PowerFunction):
        return PowerFunction(func.power - 1, func.coefficient * func.power)
    if isinstance(func, FunctionSum):
        return sum(
            map(lambda x: differentiate(x), func.constituents),
            ConstantFunction(),
        )
    if isinstance(func, Polynomial):
        return Polynomial(*map(
            lambda i, c: i * c,
            enumerate(func.coefficients)[1:]
        ))
    if isinstance(func, CharacteristicFunction):
        return WrappedFunction(lambda x: 0)
    raise NotImplementedError
