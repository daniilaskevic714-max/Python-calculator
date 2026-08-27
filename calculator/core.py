"""Ядро калькулятора: безопасный разбор и вычисление арифметических выражений.

Вместо ``eval`` используется разбор через ``ast`` с «белым списком» допустимых
узлов, поэтому выражение вида ``__import__("os")`` не сможет выполнить код.
"""

from __future__ import annotations

import ast
import math
import operator
import sys
import warnings
from decimal import (
    Decimal,
    DivisionByZero,
    InvalidOperation,
    Overflow,
    getcontext,
    localcontext,
)

getcontext().prec = 28  # точности хватает, чтобы 0.1 + 0.2 = 0.3, а не 0.30000000000000004
# Особые значения (inf/nan) и переполнение должны быть ошибкой, а не «тихим» результатом.
for _flag in (Overflow, InvalidOperation):
    getcontext().traps[_flag] = True

try:  # Python 3.11+: лимит int -> str защищает от DoS на огромных числах
    sys.set_int_max_str_digits(100_000)
except AttributeError:
    pass

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_CONSTANTS = {
    "pi": Decimal(str(math.pi)),
    "e": Decimal(str(math.e)),
}

_DISPLAY_DIGITS = 12               # значащих цифр, которые показываем
_BIG_DISPLAY = Decimal(10) ** 21   # выше этого числа выводим в экспоненциальной форме
_MAX_EXPONENT = 999                # максимальный порядок (10^999) — иначе считаем слишком большим
_MAX_LENGTH = 200                  # максимальная длина выражения, символов


class CalculatorError(ValueError):
    """Ошибка пользовательского ввода: неверное выражение или недопустимая операция."""


def _to_decimal(node: ast.Constant) -> Decimal:
    if isinstance(node.value, bool):
        raise CalculatorError("Логические значения не поддерживаются")
    if isinstance(node.value, int):
        return Decimal(node.value)
    if isinstance(node.value, float):
        return Decimal(repr(node.value))
    raise CalculatorError(f"Неизвестное значение: {node.value!r}")


def _eval_node(node: ast.AST) -> Decimal:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        return _to_decimal(node)

    if isinstance(node, ast.Name):
        try:
            return _CONSTANTS[node.id.lower()]
        except KeyError:
            raise CalculatorError(f"Неизвестный символ: {node.id!r}") from None

    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left, right = _eval_node(node.left), _eval_node(node.right)
        # 2 ^ 10^12 не просто «большое» число — его вычисление подвесит процесс.
        if isinstance(node.op, ast.Pow) and abs(right.adjusted()) > _MAX_EXPONENT:
            raise CalculatorError("Слишком большая степень (максимум 10^999)")
        try:
            return _BIN_OPS[type(node.op)](left, right)
        except (DivisionByZero, ZeroDivisionError) as exc:
            raise CalculatorError("Деление на ноль") from exc
        except (InvalidOperation, Overflow) as exc:
            raise CalculatorError("Результат слишком большой") from exc

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand))

    raise CalculatorError("Разрешены только числа, скобки и операции + - * / // % ^ **")


def _normalize(text: str) -> str:
    """Приводит ввод пользователя к синтаксису Python."""
    return (
        text.replace(",", ".")   # 2,5 -> 2.5
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")       # «длинное» минус-тире из текстовых редакторов
        .replace("^", "**")      # 2^10 -> 2 ** 10
        .replace(" ", "")
        .strip()
    )


def evaluate(expression: str) -> Decimal:
    """Вычисляет арифметическое выражение и возвращает точный результат.

    >>> evaluate("2 + 3 * 4")
    Decimal('14')
    """
    text = _normalize(expression or "")
    if not text:
        raise CalculatorError("Пустое выражение")
    if len(text) > _MAX_LENGTH:
        raise CalculatorError(f"Слишком длинное выражение (максимум {_MAX_LENGTH} символов)")

    try:
        with warnings.catch_warnings():  # ast парсер ругается SyntaxWarning на «1 if 1 else 2» и т.п.
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(text, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise CalculatorError(f"Неверное выражение: {getattr(exc, 'msg', exc)}") from exc

    return _eval_node(tree)


def _trim(digits: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
    """Убирает лишние нули в конце мантиссы; возвращает (цифры, сколько убрали)."""
    kept = len(digits)
    while kept > 1 and digits[kept - 1] == 0:
        kept -= 1
    return digits[:kept], len(digits) - kept


def _scientific(sign: int, digits: tuple[int, ...], exponent: int) -> str:
    """Экспоненциальная запись из цифр самого Decimal — без потерь ``float``."""
    trimmed, removed = _trim(digits)
    moved = exponent + removed + len(trimmed) - 1
    body = str(trimmed[0]) if len(trimmed) == 1 else f"{trimmed[0]}.{''.join(map(str, trimmed[1:]))}"
    return f"{'-' if sign else ''}{body}e{moved:+d}"


def format_result(value: Decimal) -> str:
    """Форматирует результат для показа: 12 значащих цифр, без «хвостовых» нулей."""
    if not value.is_finite():
        raise CalculatorError("Результат слишком большой")

    with localcontext() as ctx:
        ctx.prec = _DISPLAY_DIGITS
        value = +value                     # округляем ровно до того, что показываем
    sign, digits, exponent = value.as_tuple()
    trimmed, removed = _trim(digits)
    adjusted = exponent + removed + len(trimmed) - 1   # порядок числа

    if abs(adjusted) > _MAX_EXPONENT:
        raise CalculatorError("Результат слишком большой")

    if exponent >= 0:  # целое: 4, -12345, 15000000000
        number = int("".join(map(str, trimmed))) * 10 ** (exponent + removed)
        if number < _BIG_DISPLAY:
            return ("-" if sign else "") + str(number)
        return _scientific(sign, digits, exponent)

    if -4 <= adjusted < 21:  # привычная десятичная запись: 0.0009765625
        return format(value, "f").rstrip("0").rstrip(".") or "0"

    return _scientific(sign, digits, exponent)


def calculate(expression: str) -> str:
    """Точка входа для интерфейсов: строка с выражением -> строка с результатом."""
    return format_result(evaluate(expression))
