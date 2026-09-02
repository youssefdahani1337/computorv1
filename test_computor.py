import io
import unittest
from contextlib import redirect_stdout

import computor


class TestParsing(unittest.TestCase):
    def test_parse_positive_term(self):
        self.assertEqual(computor.parse_term("5 * X^0"), (5.0, 0))

    def test_parse_negative_decimal_term(self):
        self.assertEqual(computor.parse_term("-9.3 * X^2"), (-9.3, 2))

    def test_reject_free_form_term(self):
        with self.assertRaises(ValueError):
            computor.parse_term("9")

    def test_parse_zero_side(self):
        self.assertEqual(computor.parse_side("0"), {})

    def test_combine_repeated_exponents(self):
        result = computor.parse_side(
            "5 * X^0 + 4 * X^2 - 9.3 * X^2"
        )
        self.assertEqual(result[0], 5.0)
        self.assertAlmostEqual(result[2], -5.3)

    def test_reduce_both_sides(self):
        result = computor.parse_equation(
            "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"
        )
        self.assertEqual(result, {0: 4.0, 1: 4.0, 2: -9.3})

    def test_equation_requires_equal_sign(self):
        with self.assertRaises(ValueError):
            computor.parse_equation("5 * X^0")

    def test_equation_rejects_multiple_equal_signs(self):
        with self.assertRaises(ValueError):
            computor.parse_equation("5 * X^0 = 0 = 0")

    def test_equation_rejects_empty_side(self):
        with self.assertRaises(ValueError):
            computor.parse_equation("5 * X^0 = ")


class TestMathHelpers(unittest.TestCase):
    def test_square_root_zero(self):
        self.assertEqual(computor.square_root(0), 0.0)

    def test_square_root_integer(self):
        self.assertAlmostEqual(computor.square_root(25), 5.0, places=7)

    def test_square_root_decimal(self):
        self.assertAlmostEqual(computor.square_root(2), 2 ** 0.5, places=7)

    def test_square_root_rejects_negative_number(self):
        with self.assertRaises(ValueError):
            computor.square_root(-1)

    def test_degree_zero_for_empty_polynomial(self):
        self.assertEqual(computor.get_polynomial_degree({}), 0)

    def test_ignore_zero_highest_coefficient(self):
        coefficients = {0: 2.0, 1: 3.0, 2: 0.0}
        self.assertEqual(computor.get_polynomial_degree(coefficients), 1)

    def test_degree_greater_than_two(self):
        coefficients = {0: 1.0, 3: -5.6}
        self.assertEqual(computor.get_polynomial_degree(coefficients), 3)


class TestSolver(unittest.TestCase):
    @staticmethod
    def capture_solution(equation):
        coefficients = computor.parse_equation(equation)
        output = io.StringIO()

        with redirect_stdout(output):
            computor.solve(coefficients)

        return output.getvalue()

    def test_any_real_number_is_solution(self):
        output = self.capture_solution("6 * X^0 = 6 * X^0")
        self.assertIn("Any real number is a solution", output)

    def test_constant_equation_has_no_solution(self):
        output = self.capture_solution("10 * X^0 = 15 * X^0")
        self.assertIn("No solution", output)

    def test_degree_one(self):
        output = self.capture_solution("5 * X^0 + 4 * X^1 = 4 * X^0")
        self.assertIn("Polynomial degree: 1", output)
        self.assertIn("-0.25", output)

    def test_degree_two_positive_discriminant(self):
        output = self.capture_solution(
            "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"
        )
        self.assertIn("strictly positive", output)
        self.assertIn("0.905", output)
        self.assertIn("-0.475", output)

    def test_degree_two_zero_discriminant(self):
        output = self.capture_solution(
            "1 * X^0 + 2 * X^1 + 1 * X^2 = 0"
        )
        self.assertIn("Discriminant is zero", output)
        self.assertIn("-1", output)

    def test_degree_two_negative_discriminant(self):
        output = self.capture_solution(
            "1 * X^0 + 2 * X^1 + 5 * X^2 = 0"
        )
        self.assertIn("strictly negative", output)
        self.assertIn("i", output)

    def test_degree_greater_than_two(self):
        output = self.capture_solution(
            "8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 3 * X^0"
        )
        self.assertIn("Polynomial degree: 3", output)
        self.assertIn("can't solve", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
