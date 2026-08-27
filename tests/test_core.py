"""Тесты ядра калькулятора.

Запуск:  python -m unittest discover -s tests -v     (или pytest, если установлен)
"""

from __future__ import annotations

import unittest
from decimal import Decimal

from calculator.core import CalculatorError, calculate, evaluate


class TestArithmetic(unittest.TestCase):
    def test_basic_operations(self) -> None:
        self.assertEqual(calculate("2 + 3 * 4"), "14")
        self.assertEqual(calculate("(2 + 3) * 4"), "20")
        self.assertEqual(calculate("10 - 2.5"), "7.5")
        self.assertEqual(calculate("10 / 4"), "2.5")
        self.assertEqual(calculate("7 // 2"), "3")
        self.assertEqual(calculate("7 % 3"), "1")

    def test_unary_minus(self) -> None:
        self.assertEqual(calculate("-5 + 2"), "-3")
        self.assertEqual(calculate("-(3 * 3)"), "-9")

    def test_power_variants(self) -> None:
        self.assertEqual(calculate("2^10"), "1024")
        self.assertEqual(calculate("2 ** 10"), "1024")
        self.assertEqual(calculate("9 ^ 0.5"), "3")

    def test_unicode_input(self) -> None:
        self.assertEqual(calculate("6 × 7"), "42")
        self.assertEqual(calculate("9 ÷ 3"), "3")
        self.assertEqual(calculate("5 − 8"), "-3")

    def test_comma_as_decimal_separator(self) -> None:
        self.assertEqual(calculate("2,5 + 1"), "3.5")

    def test_no_binary_floating_errors(self) -> None:
        self.assertEqual(calculate("0.1 + 0.2"), "0.3")

    def test_constants(self) -> None:
        self.assertEqual(calculate("pi"), "3.14159265359")
        self.assertEqual(evaluate("e").quantize(Decimal("0.001")), Decimal("2.718"))


class TestErrors(unittest.TestCase):
    def test_division_by_zero(self) -> None:
        with self.assertRaises(CalculatorError) as ctx:
            calculate("1 / 0")
        self.assertIn("ноль", str(ctx.exception).lower())

    def test_empty_expression(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("")
        with self.assertRaises(CalculatorError):
            calculate("   ")

    def test_unbalanced_brackets(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("(2 + 3")

    def test_letters_rejected(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("a + 2")

    def test_no_code_execution(self) -> None:
        for attack in (
            "__import__('os').system('id')",
            "open('/etc/passwd').read()",
            "1 if 1 else 2",
            "[i for i in range(10)]",
            "().__class__",
        ):
            with self.subTest(attack=attack):
                with self.assertRaises(CalculatorError):
                    calculate(attack)

    def test_no_silent_infinity(self) -> None:
        for expr in ("1 / 0 * 0", "0 / 0", "1 / 0 % 1"):
            with self.subTest(expr=expr):
                with self.assertRaises(CalculatorError):
                    calculate(expr)

    def test_explosion_in_power_is_rejected(self) -> None:
        # показатель 10^2000 потребовал бы квадриллионы цифр — вычислять нельзя
        with self.assertRaises(CalculatorError):
            calculate("2 ^ (10 ^ 2000)")

    def test_too_long_expression(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("1+" * 300)

    def test_huge_result_is_shown_in_scientific_notation(self) -> None:
        self.assertEqual(calculate("10 ^ 400"), "1e+400")
        self.assertEqual(calculate("(-10) ^ 401"), "-1e+401")

    def test_big_result_rendered_in_exponential_form(self) -> None:
        self.assertEqual(calculate("10 ^ 30"), "1e+30")
        self.assertEqual(calculate("2 ^ 100"), "1.26765060023e+30")
        self.assertEqual(calculate("1 / (10 ^ 30)"), "1e-30")


class TestFormatting(unittest.TestCase):
    def test_integer_result_has_no_dot(self) -> None:
        self.assertEqual(calculate("4 / 2"), "2")

    def test_float_precision(self) -> None:
        self.assertEqual(calculate("1 / 3"), "0.333333333333")
        self.assertEqual(calculate("2 / 3"), "0.666666666667")


if __name__ == "__main__":
    unittest.main()
