from decimal import Decimal


def minimum(a, b):
    if a <= b:
        return a
    return b


def maximum(a, b):
    if a >= b:
        return a
    return b


def output_range(func, lower, upper, resolution=100):
    lower_decimal = Decimal(str(lower))
    upper_decimal = Decimal(str(upper))
    lower_val = func(lower_decimal)
    upper_val = func(upper_decimal)
    abs_minimum = minimum(lower_val, upper_val)
    abs_maximum = maximum(lower_val, upper_val)
    absolute_minima = [
        lower_decimal if lower_val == abs_minimum else upper_decimal]
    absolute_maxima = [
        lower_decimal if lower_val == abs_maximum else upper_decimal]
    for n in range(1, resolution):
        x = lower_decimal + (upper_decimal - lower_decimal) * n / Decimal(
            str(resolution))
        val = func(x)
        new_minimum = minimum(abs_minimum, val)
        if new_minimum < abs_minimum:
            absolute_minima = [x]
            abs_minimum = new_minimum
        elif val == new_minimum:
            absolute_minima.append(x)
        else:
            new_maximum = maximum(abs_maximum, val)
            if new_maximum > abs_maximum:
                abs_maximum = new_maximum
                absolute_maxima = [x]
            elif new_maximum == val:
                absolute_maxima.append(x)
    return abs_minimum, abs_maximum, absolute_minima, absolute_maxima


def get_local_extrema(func, a, b, resolution=100):
    last_direction = 0
    last_x = Decimal(str(a))
    last_val = func(last_x)
    local_extrema = []
    for n in range(1, resolution + 1):
        x = Decimal(str(a)) + (Decimal(str(b)) - Decimal(str(a))) * n \
                / resolution
        val = func(x)
        direction = val - last_val

        if last_direction <= 0 and direction > 0:
            local_extrema.append(last_x)
        if last_direction >= 0 and direction < 0:
            local_extrema.append(last_x)
        last_x = x
        last_val = val
        last_direction = direction
    local_extrema.append(b)
    return local_extrema
