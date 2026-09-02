import re
import sys


TERM_PATTERN = re.compile(
    r"([+-]?\s*\d+(?:\.\d+)?)\s*\*\s*X\^(\d+)"
)
EPSILON = 1e-9

def parse_term(term):
    """
    Parse:
        -9.3 * X^2

    Return:
        (-9.3, 2)
    """

    match = TERM_PATTERN.fullmatch(term.strip())

    if not match:
        raise ValueError(f"Invalid term: {term}")

    coefficient = float(match.group(1).replace(" ", ""))
    exponent = int(match.group(2))

    return coefficient, exponent


def parse_side(side):
    """
    Parse one side of the equation.

    Example:
        5 * X^0 + 4 * X^1 - 9.3 * X^2

    Return:
        {0: 5.0, 1: 4.0, 2: -9.3}
    """

    side = side.strip()

    # The subject allows: "... = 0"
    if side == "0":
        return {}

    coefficients = {}

    # Convert subtraction into addition of a negative term
    normalized_side = side.replace("-", "+-")
    terms = normalized_side.split("+")

    for term in terms:
        term = term.strip()

        if not term:
            continue

        coefficient, exponent = parse_term(term)

        coefficients[exponent] = (
            coefficients.get(exponent, 0.0) + coefficient
        )

    return coefficients


def split_equation(equation):
    """
    Split the equation into its left and right sides.
    """

    if equation.count("=") != 1:
        raise ValueError(
            "The equation must contain exactly one '='"
        )

    left_side, right_side = equation.split("=")

    left_side = left_side.strip()
    right_side = right_side.strip()

    if not left_side or not right_side:
        raise ValueError(
            "Both sides of the equation must be non-empty"
        )

    return left_side, right_side


def reduce_equation(left, right):
    """
    Move everything to the left:

        left - right = 0
    """

    reduced = {}
    all_exponents = set(left) | set(right)

    for exponent in all_exponents:
        reduced[exponent] = (
            left.get(exponent, 0.0)
            - right.get(exponent, 0.0)
        )

    return reduced


def parse_equation(equation):
    """
        5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0
    """

    # left_side = "5 * X^0 + 4 * X^1 - 9.3 * X^2"
    # right_side = "1 * X^0"
    left_side, right_side = split_equation(equation) 


    #left_coefficients = {0: 5.0, 1: 4.0, 2: -9.3}
    #right_coefficients = {0: 1.0}
    left_coefficients = parse_side(left_side)
    right_coefficients = parse_side(right_side)

    # equation: 5 * X^0 + 4 * X^1 - 9.3 * X^2 - 1 * X^0 = 0
    reduced_coefficients = reduce_equation(
        left_coefficients,
        right_coefficients
    )

    return reduced_coefficients


def absolute(number):
    if number < 0:
        return -number

    return number

def is_zero(number):
    return absolute(number) < EPSILON


def square_root(number):
    """
    Calculate square root using Newton's method.
    This avoids using math.sqrt().
    """

    if number < 0:
        raise ValueError(
            "Cannot calculate the real square root of a negative number"
        )

    if is_zero(number):
        return 0.0

    guess = number if number >= 1 else 1.0

    while True:
        new_guess = (guess + number / guess) / 2

        if absolute(new_guess - guess) < EPSILON:
            return new_guess

        guess = new_guess


def format_number(number):
    """
    Format numbers cleanly:
        4.0       -> 4
        -0.0      -> 0
        0.905239  -> 0.905239
    """

    if is_zero(number):
        return "0"

    nearest_integer = int(number)

    if is_zero(number - nearest_integer):
        return str(nearest_integer)

    return f"{number:.6f}".rstrip("0").rstrip(".")


def get_polynomial_degree(coefficients):
    """
    Find the highest exponent having a non-zero coefficient.
    """

    non_zero_exponents = [
        exponent
        for exponent, coefficient in coefficients.items()
        if not is_zero(coefficient)
    ]

    if not non_zero_exponents:
        return 0

    return max(non_zero_exponents)


def print_form(coefficients):
    """
    Print:
        Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0
    """

    if not coefficients:
        print("Reduced form: 0 * X^0 = 0")
        return

    highest_exponent = max(coefficients)
    parts = []

    for exponent in range(highest_exponent + 1):
        coefficient = coefficients.get(exponent, 0.0)
        value = format_number(absolute(coefficient))

        term = f"{value} * X^{exponent}"

        if not parts:
            if coefficient < 0:
                parts.append(f"-{term}")
            else:
                parts.append(term)

        elif coefficient < 0:
            parts.append(f"- {term}")

        else:
            parts.append(f"+ {term}")

    print(f"Reduced form: {' '.join(parts)} = 0")


def solve_degree_zero(coefficients):
    constant = coefficients.get(0, 0.0)

    if is_zero(constant):
        print("Any real number is a solution.")
    else:
        print("No solution.")


def solve_degree_one(coefficients):
    # bX + c = 0
    coefficient_b = coefficients.get(1, 0.0)
    coefficient_c = coefficients.get(0, 0.0)

    solution = -coefficient_c / coefficient_b

    print("The solution is:")
    print(format_number(solution))


def solve_degree_two(coefficients):
    # aX² + bX + c = 0
    coefficient_a = coefficients.get(2, 0.0)
    coefficient_b = coefficients.get(1, 0.0)
    coefficient_c = coefficients.get(0, 0.0)

    # D = b² - 4ac
    discriminant = (coefficient_b * coefficient_b - 4 * coefficient_a * coefficient_c)

    if discriminant > EPSILON:
        root = square_root(discriminant)

        solution_one = (-coefficient_b + root ) / (2 * coefficient_a)

        solution_two = ( -coefficient_b - root ) / (2 * coefficient_a)

        print("Discriminant is strictly positive")
        print("the two solutions are:" )
        print(format_number(solution_one))
        print(format_number(solution_two))

    elif discriminant < -EPSILON:
        real_part = ( -coefficient_b ) / (2 * coefficient_a)

        imaginary_part = ( square_root(-discriminant) / absolute(2 * coefficient_a) )

        print( "Discriminant is strictly negative, ")
        print ("the two complex solutions are:")
        print("the two complex solutions are:")
        print("the two complex solutions are:")

        print(
            f"{format_number(real_part)} "
            f"+ {format_number(imaginary_part)}i"
        )

        print(
            f"{format_number(real_part)} "
            f"- {format_number(imaginary_part)}i"
        )

    else:
        solution = (
            -coefficient_b
        ) / (2 * coefficient_a)

        print(
            "Discriminant is zero, "
            "the solution is:"
        )
        print(format_number(solution))


def solve(coefficients):
    print_form(coefficients)

    degree = get_polynomial_degree(coefficients)

    if degree == 0:
        solve_degree_zero(coefficients)
        return

    print(f"Polynomial degree: {degree}")

    if degree == 1:
        solve_degree_one(coefficients)

    elif degree == 2:
        solve_degree_two(coefficients)

    else:
        print("The polynomial degree is strictly greater than 2, ")
        print ("Can't solve this equation.")
def main():
    try:
        if len(sys.argv) == 1:
            equation = input("Please enter the equation:\n")

        elif len(sys.argv) == 2:
            equation = sys.argv[1]

        else:
            raise ValueError("please provide a single equation as an argument")

        coefficients = parse_equation(equation)
        solve(coefficients)

    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()