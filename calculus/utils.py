from custom_numbers.computation import Number
from custom_numbers.utils import minimum, maximum


def output_range(func, lower, upper, resolution=100):
    # Convert lower and upper bounds to decimals to make arithmetic more
    # predictable (eg dividing values into intervals can be precise with
    # decimals when it isn't necessarily with binary representations)
    lower_in = Number.of(lower)
    upper_in = Number.of(upper)

    # Capture the outputs at the lower and upper endpoints
    lower_val = func(lower_in)
    upper_val = func(upper_in)

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
        x = lower_in + (upper_in - lower_in) * n / resolution
        val = func(x)
        abs_minimum = minimum(abs_minimum, val)
        abs_maximum = maximum(abs_maximum, val)
    return abs_minimum, abs_maximum


def get_local_extrema(func, a, b, resolution=100):
    last_direction = 0
    a_in = Number.of(a)
    b_in = Number.of(b)
    last_x = a_in
    last_val = func(last_x)
    local_extrema = []
    for n in range(1, resolution + 1):
        x = a_in \
            + (b_in - a_in) * n / resolution
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
