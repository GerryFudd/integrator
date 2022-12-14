from algebra.linear.equations import MultiDimensionalEquation
from algebra.linear.subspace import LinearSystem, KnownValue
from custom_numbers.exact.rational_number import RationalNumber


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
        return PSquareSide(p, direction, *map(lambda n: ({direction.move(start, n): 1}, 0), range(p)))

    @staticmethod
    def left(p: int, *mappings: tuple[dict[tuple[int, int], int], int]):
        return PSquareSide(p, Direction.left(), *mappings)

    @staticmethod
    def top(p: int, *mappings: tuple[dict[tuple[int, int], int], int]):
        return PSquareSide(p, Direction.up(), *mappings)

    @staticmethod
    def bottom(p: int, *mappings: tuple[dict[tuple[int, int], int], int]):
        return PSquareSide(p, Direction.down(), *mappings)

    @staticmethod
    def right(p: int, *mappings: tuple[dict[tuple[int, int], int], int]):
        return PSquareSide(p, Direction.right(), *mappings)

    def __init__(self, p: int, direction: Direction, *mappings: tuple[dict[tuple[int, int], int], int]):
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
        start_vals: dict[tuple[int, int], int] = None,
        is_terminus: bool = False,
    ):
        self.p = p
        self.left_seed = or_else(left_seed, PSquareSide.zero(p, Direction.right()))
        self.top_seed = or_else(top_seed, PSquareSide.zero(p, Direction.down()))
        self.start_vals = or_else(start_vals, {})
        self.is_terminus = is_terminus

    def get_equation_mapping(self, x: int, y: int) -> tuple[dict[tuple[int, int], int], int] | None:
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
        linear_system: LinearSystem[tuple[int, int]]
    ):
        self.p = p
        self.linear_system: LinearSystem[tuple[int, int]] = linear_system
        self.__known_values: dict[tuple[int, int], KnownValue[tuple[int, int]]] | None = None

    def __str__(self):
        return str(self.linear_system)

    def __repr__(self):
        return f'PSquareResult(p={self.p},linear_system={self.linear_system})'

    @staticmethod
    def extract_mapping(eq: MultiDimensionalEquation) -> tuple[dict[tuple[int, int], int], int]:
        result = {}
        for m, position, coefficient in eq:
            if coefficient == 0:
                continue
            result[position] = coefficient
        return result, eq.value

    @property
    def right(self):
        mappings = []
        while len(mappings) < self.p:
            mappings.append(({}, 0))
        for _, eq in self.linear_system:
            first_non_zero = eq.first_non_zero
            if first_non_zero < len(self.linear_system.variables):
                x, y = self.linear_system.variables[first_non_zero]
                if y == self.p - 1:
                    mappings[x] = self.extract_mapping(eq)
        return PSquareSide.right(self.p, *mappings)

    @property
    def bottom(self):
        mappings = []
        while len(mappings) < self.p:
            mappings.append(({}, 0))
        for _, eq in self.linear_system:
            first_non_zero = eq.first_non_zero
            if first_non_zero < len(self.linear_system.variables):
                x, y = self.linear_system.variables[first_non_zero]
                if x == self.p - 1:
                    mappings[y] = self.extract_mapping(eq)
        return PSquareSide.bottom(self.p, *mappings)

    @staticmethod
    def extract_known(eq: MultiDimensionalEquation[tuple[int, int]]) -> tuple[tuple[int, int] | None, int | None]:
        coordinates: tuple[int, int] | None = None
        coefficient: int | None = None
        for _, coord, coeff in eq:
            if coeff == 0:
                continue
            if coordinates is None:
                coordinates = coord
                coefficient = coeff
                continue
            return None, None
        return coordinates, coefficient

    @property
    def additional_values(self) -> dict[tuple[int, int], int]:
        result = {}
        for _, eq in self.linear_system:
            coordinates, coefficient = self.extract_known(eq)
            if coordinates is not None and (coordinates[0] < 0 or coordinates[1] < 0):
                result[coordinates] = eq.value
                if coefficient != 1:
                    result[coordinates] /= coefficient

        return result

    @property
    def known_values(self) -> dict[tuple[int, int], KnownValue[tuple[int, int]]]:
        if self.__known_values is None:
            self.__known_values = self.linear_system.known_values()
        return self.__known_values

    def get_values(self) -> dict[tuple[int, int], KnownValue[tuple[int, int]]]:
        known_values = self.known_values
        if len(known_values) < self.p**2:
            raise NotEnoughInformation
        return known_values

    def with_values(self, *values: tuple[tuple[int, int], int]):
        return PSquareResult(
            self.p,
            LinearSystem(
                *self.linear_system.equations,
                *map(lambda x: MultiDimensionalEquation({x[0]: 1}, x[1], self.linear_system.variables), values),
            ).solve()
        )


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

    return PSquareResult(
        seed.p,
        linear_system.solve()
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


def solve_full_system(p: int) -> dict[tuple[int, int], int | RationalNumber]:
    overall_result = []
    while len(overall_result) < p:
        current_row = []
        while len(current_row) < min(len(overall_result), p-len(overall_result)):
            coordinates = (len(overall_result), len(current_row))
            source_vals = overall_result[coordinates[1]][coordinates[0]].get_values()
            equation_mappings = []
            variables = []
            for n in range(p):
                for m in range(p):
                    variables.append((n, m))
                    value, coefficient = source_vals[(m, n)].reduced()
                    equation_mappings.append(({(n, m): coefficient}, value))
            current_row.append(PSquareResult(
                p, LinearSystem(*map(lambda x: MultiDimensionalEquation(x[0], x[1], variables), equation_mappings))
            ))
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
        d = 1
        while len(additional_values) > 0:
            n = len(current_row) - d - 1
            new_values = {}
            mapped_values = []
            for key, val in additional_values.items():
                adjusted_key = (0, key[1] + p * d)
                mapped_values.append((adjusted_key, val))
                if adjusted_key[1] != 0:
                    new_values[key] = val
            current_row[n] = current_row[n].with_values(*mapped_values)
            d += 1
            additional_values = new_values

        overall_result.append(current_row)
    result: dict[tuple[int, int], int | RationalNumber] = {}
    for n in range(p**2):
        for m in range(p**2):
            a, b = divmod(n, p)
            c, d = divmod(m, p)
            current_row = overall_result[a]
            if len(current_row) <= c:
                continue
            current_square_values = current_row[c].known_values
            result[(n, m)] = current_square_values[(b, d)].value
    return result
