from algebra.linear.equations import MultiDimensionalEquation
from algebra.linear.subspace import LinearSystem, Point
from custom_numbers.types import Numeric


class NotEnoughInformation(Exception):
    pass


class Direction:
    @staticmethod
    def down():
        return Direction(0, 1)

    @staticmethod
    def up():
        return Direction(0, -1)

    @staticmethod
    def right():
        return Direction(1, 1)

    @staticmethod
    def left():
        return Direction(1, -1)

    def __init__(self, coordinate: int, orientation: int):
        self.coordinate = coordinate
        self.orientation = orientation

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self.coordinate == 0:
            if self.orientation > 0:
                return 'down'
            return 'up'
        if self.orientation > 0:
            return 'right'
        return 'left'

    @property
    def symbol(self):
        if self.coordinate == 0:
            if self.orientation > 0:
                return 'V'
            return '^'
        if self.orientation > 0:
            return '>'
        return '<'

    def move(self, point: tuple[int, int], distance: int = 1):
        if self.coordinate == 0:
            return point[0] + self.orientation * distance, point[1]
        return point[0], point[1] + self.orientation * distance

    def move_perp(self, point: tuple[int, int], distance: int = 1):
        if self.coordinate == 0:
            return point[0], point[1] + distance
        return point[0] + distance, point[1]


def default_point_mapping(point: tuple[int, int]):
    return {
        (point[0] - 1, point[1]): 1,
        point: 1,
        (point[0], point[1] - 1): 1,
    }, 0


def or_else(value, default):
    if value is None:
        return default
    return value


class PSquareSide:
    @staticmethod
    def zero(p: int, direction: Direction):
        if direction.orientation < 0:
            start = (0, 0)
        else:
            start = direction.move_perp((0, 0), p-1)
        return PSquareSide(p, direction, *map(lambda n: ({direction.move_perp(start, n): 1}, 0), range(p)))

    @staticmethod
    def left(p: int, *mappings: tuple[dict[tuple[int, int], Numeric], Numeric]):
        return PSquareSide(p, Direction.left(), *mappings)

    @staticmethod
    def top(p: int, *mappings: tuple[dict[tuple[int, int], Numeric], Numeric]):
        return PSquareSide(p, Direction.up(), *mappings)

    @staticmethod
    def bottom(p: int, *mappings: tuple[dict[tuple[int, int], Numeric], Numeric]):
        return PSquareSide(p, Direction.down(), *mappings)

    @staticmethod
    def right(p: int, *mappings: tuple[dict[tuple[int, int], Numeric], Numeric]):
        return PSquareSide(p, Direction.right(), *mappings)

    def __init__(self, p: int, direction: Direction, *mappings: tuple[dict[tuple[int, int], Numeric], Numeric]):
        self.p = p
        self.direction = direction
        self.mappings = list(mappings)

    def __str__(self):
        return f'{self.direction.symbol}{self.mappings}{self.direction.symbol}'

    def __getitem__(self, item):
        new_mapping = {}
        base_mapping, value = self.mappings[item]
        for key, coefficient in base_mapping.items():
            new_mapping[self.direction.move(key, -self.p)] = coefficient

        return new_mapping, value


class PSquareSeed:
    @staticmethod
    def first_square(p: int):
        return PSquareSeed(
            p,
            start_vals={(0, 0): 1}
        )

    def __init__(
        self, p: int,
        left_seed: PSquareSide = None,
        top_seed: PSquareSide = None,
        start_vals: dict[tuple[int, int], Numeric] = None,
        is_terminus: bool = False,
    ):
        self.p = p
        self.left_seed = or_else(left_seed, PSquareSide.zero(p, Direction.right()))
        self.top_seed = or_else(top_seed, PSquareSide.zero(p, Direction.down()))
        self.start_vals = or_else(start_vals, {})
        self.is_terminus = is_terminus

    def get_equation_mapping(self, x: int, y: int) -> tuple[dict[tuple[int, int], Numeric], Numeric] | None:
        if x == 0:
            side = self.top_seed
            base_mapping = side[y]
        elif y == 0:
            side = self.left_seed
            base_mapping = side[x]
        else:
            return default_point_mapping((x, y))
        # base_mapping: u+factor*matching_key=value -> factor*matching_key=value-u
        # identity: neighbor+self+matching_key=0 -> factor*matching_key=-factor*neighbor-factor*self
        # factor*neighbor+factor*self-u=-value
        new_mapping = {}
        matching_key = side.direction.move((x, y), -1)
        neighbor_key = side.direction.move_perp((x, y), -1)
        factor = 0
        for key, coefficient in base_mapping[0].items():
            if key == matching_key:
                factor = coefficient
            else:
                new_mapping[key] = -coefficient
        if factor == 0:
            return {neighbor_key: 1, (x, y): 1}, 0
        new_mapping[neighbor_key] = factor
        new_mapping[(x, y)] = factor
        return new_mapping, -base_mapping[1]


class PSquareResult:
    def __init__(
        self,
        p: int,
        left: PSquareSide,
        top: PSquareSide,
        right: PSquareSide,
        bottom: PSquareSide,
        known_values: dict[tuple[int, int], Numeric] = None,
        additional_values: dict[tuple[int, int], Numeric] = None,
    ):
        self.p = p
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.known_values = or_else(known_values, {})
        self.additional_values = or_else(additional_values, {})

    def __str__(self):
        return f'{self.known_values} {self.left} {self.top} {self.right} {self.bottom}'

    def __repr__(self):
        return f'PSquareResult(p={self.p},left={self.left},top={self.top},bottom={self.bottom},right={self.right},' \
               f'known_values={self.known_values})'

    def get_values(self) -> list[list[Numeric]]:
        if len(self.known_values) < self.p**2:
            raise NotEnoughInformation
        result = []
        while len(result) < self.p:
            row = []
            while len(row) < self.p:
                new_point = (len(result), len(row))
                if new_point not in self.known_values:
                    raise NotEnoughInformation
                row.append(self.known_values[new_point])
            result.append(row)
        return result


def p_square(seed: PSquareSeed) -> PSquareResult:
    linear_system: LinearSystem[tuple[int, int]] | None = None
    for x in range(seed.p):
        for y in range(seed.p):
            mappings = []
            if x != 0 or y != 0:
                mappings.append(seed.get_equation_mapping(x, y))
            if (x, y) in seed.start_vals:
                mappings.append(({(x, y): 1}, seed.start_vals[(x, y)]))
            if seed.is_terminus and x + y >= seed.p:
                mappings.append(({(x, y): 1}, 0))
            if linear_system is None and len(mappings) > 0:
                linear_system = LinearSystem(*map(lambda u: MultiDimensionalEquation.of_mapping(u[0], u[1]), mappings))
            else:
                for mapping, val in mappings:
                    linear_system.merge_mapping(mapping, val)

    variables = linear_system.variables.copy()
    variables.remove((0, 0))
    end_variables = [(0, 0)]
    for a, b in linear_system.variables:
        if a < 0 or b < 0:
            variables.remove((a, b))
            end_variables.append((a, b))
    linear_system = linear_system.with_vars(variables + sorted(end_variables, reverse=True))

    solved_linear_system = linear_system.solve()
    if isinstance(solved_linear_system, Point):
        additional_values = {}
        left_mappings = []
        right_mappings = []
        top_mappings = []
        bottom_mappings = []
        for n, coordinates, value in solved_linear_system:
            if coordinates[0] < 0 or coordinates[0] >= seed.p or coordinates[1] < 0 or coordinates[1] >= seed.p:
                additional_values[coordinates] = value
                continue
            if coordinates[0] == 0:
                top_mappings.append(({coordinates: 1}, value))
            elif coordinates[0] == seed.p-1:
                bottom_mappings.append(({coordinates: 1}, value))
            if coordinates[1] == 0:
                left_mappings.append(({coordinates: 1}, value))
            elif coordinates[1] == seed.p-1:
                right_mappings.append(({coordinates: 1}, value))
        return PSquareResult(
            seed.p,
            left=PSquareSide.left(seed.p, *left_mappings),
            right=PSquareSide.right(seed.p, *right_mappings),
            top=PSquareSide.top(seed.p, *top_mappings),
            bottom=PSquareSide.bottom(seed.p, *bottom_mappings),
            known_values=solved_linear_system.variable_mapping,
            additional_values=additional_values
        )

    left_side_mappings = {0: ({}, 0)}
    top_side_mappings = {0: ({}, 0)}
    bottom_side_mappings = {}
    right_side_mappings = {}
    known_values = {}

    for n, eq in solved_linear_system:
        new_mapping = {}
        first_non_zero = None
        for m, position, coefficient in eq:
            if coefficient == 0:
                continue
            if first_non_zero is None:
                first_non_zero = position
            new_mapping[position] = coefficient
        if len(new_mapping) == 1:
            for key, coeff in new_mapping.items():
                known_values[key] = eq.value / coeff
        if first_non_zero[0] == 0:
            top_side_mappings[first_non_zero[1]] = (new_mapping, eq.value)
        elif first_non_zero[0] == seed.p-1:
            bottom_side_mappings[first_non_zero[1]] = (new_mapping, eq.value)

        if first_non_zero[1] == 0:
            left_side_mappings[first_non_zero[0]] = (new_mapping, eq.value)
        elif first_non_zero[1] == seed.p-1:
            right_side_mappings[first_non_zero[0]] = (new_mapping, eq.value)

    return PSquareResult(
        seed.p,
        left=PSquareSide.left(seed.p, *map(lambda k: left_side_mappings[k], sorted(left_side_mappings.keys()))),
        top=PSquareSide.top(seed.p, *map(lambda k: top_side_mappings[k], sorted(top_side_mappings.keys()))),
        bottom=PSquareSide.bottom(seed.p, *map(lambda k: bottom_side_mappings[k], sorted(bottom_side_mappings.keys()))),
        right=PSquareSide.right(seed.p, *map(lambda k: right_side_mappings[k], sorted(right_side_mappings.keys()))),
        known_values=known_values
    )


def get_top_seed(overall_result: list[list[PSquareResult]], n: int):
    if not overall_result:
        return None
    return overall_result[-1][n].bottom


def get_left_seed(current_row: list[PSquareResult], n: int = None):
    if n is None:
        if len(current_row) == 0:
            return None
        return current_row[-1].right
    if n == 0:
        return None
    return current_row[n-1].right


def solve_full_system(p: int):
    overall_result = []
    while len(overall_result) < p:
        current_row = []
        while len(current_row) < min(len(overall_result), p-len(overall_result)):
            coordinates = (len(overall_result), len(current_row))
            source_vals = overall_result[coordinates[1]][coordinates[0]].get_values()
            current_start_vals = {}
            for n in range(p):
                for m in range(p):
                    current_start_vals[(n, m)] = source_vals[m][n]
            left_seed = get_left_seed(current_row)
            top_seed = get_top_seed(overall_result, len(current_row))
            current_row.append(p_square(PSquareSeed(
                p, left_seed=left_seed, top_seed=top_seed, start_vals=current_start_vals
            )))
        if len(current_row) + len(overall_result) == p:
            overall_result.append(current_row)
            continue
        while len(current_row) < p-len(overall_result)-1:
            if not overall_result and not current_row:
                current_row.append(p_square(PSquareSeed.first_square(p)))
                continue
            top_seed = get_top_seed(overall_result, len(current_row))
            left_seed = get_left_seed(current_row)
            current_row.append(p_square(PSquareSeed(
                p, left_seed=left_seed, top_seed=top_seed,
            )))

        current_row.append(p_square(PSquareSeed(
            p, left_seed=get_left_seed(current_row), top_seed=get_top_seed(overall_result, len(current_row)),
            is_terminus=True
        )))
        additional_values = current_row[-1].additional_values
        for key in sorted(additional_values.keys()):
            n = len(current_row) - 1 + key[1]//p
            current_row[n] = p_square(PSquareSeed(
                p, left_seed=get_left_seed(current_row, n), top_seed=get_top_seed(overall_result, n),
                start_vals={(0, 0): additional_values[key]},
            ))
        overall_result.append(current_row)
    result = Point.builder()
    for n in range(p**2):
        for m in range(p**2):
            a, b = divmod(n, p)
            c, d = divmod(m, p)
            current_row = overall_result[a]
            if len(current_row) <= c:
                continue
            current_square_values = current_row[c].known_values
            result.map((n, m), current_square_values[(b, d)])
    return result.build()
