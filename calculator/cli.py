"""Интерфейс для терминала.

Запуск:  python -m calculator            (режим REPL)
         python -m calculator "2+2*3"    (разовый расчёт)
"""

from __future__ import annotations

import sys
from decimal import Decimal

from .core import CalculatorError, calculate, evaluate, format_result

_BANNER = """Мини-калькулятор. Поддержка: +  -  *  /  //  %  ^  скобки, pi, e, ans.
Введите 'help' для справки, 'exit' — чтобы выйти."""

_HELP = """Примеры:
  2 + 3 * 4          -> 14
  (2 + 3) * 4        -> 20
  10 / 4             -> 2.5
  2^10               -> 1024
  0.1 + 0.2          -> 0.3
  pi * 2             -> 6.28318530718
  ans * 2            -> удвоить предыдущий результат
  history            -> показать историю
  clear              -> очистить историю
  exit | quit        -> выход"""


def _evaluate_with_memory(text: str, ans: Decimal | None) -> str:
    """Подставляет предыдущий результат вместо слова ``ans``."""
    if "ans" in text.lower():
        if ans is None:
            raise CalculatorError("Нет предыдущего результата (ans)")
        text = text.lower().replace("ans", str(ans))
    return format_result(evaluate(text))


def repl() -> int:
    print(_BANNER)
    history: list[str] = []
    ans: Decimal | None = None

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        match line.lower():
            case "exit" | "quit" | "q":
                break
            case "help":
                print(_HELP)
                continue
            case "history":
                if not history:
                    print("  история пуста")
                else:
                    print("\n".join(f"  {i + 1:>2}. {row}" for i, row in enumerate(history)))
                continue
            case "clear":
                history.clear()
                print("  история очищена")
                continue

        try:
            result = _evaluate_with_memory(line, ans)
        except CalculatorError as exc:
            print(f"  ошибка: {exc}")
            continue

        if "ans" in line.lower() and ans is not None:
            ans = evaluate(line.lower().replace("ans", str(ans)))
        else:
            ans = evaluate(line)
        history.append(f"{line} = {result}")
        print(f"  = {result}")

    print("Пока!")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        try:
            print(calculate(" ".join(args)))
            return 0
        except CalculatorError as exc:
            print(f"ошибка: {exc}", file=sys.stderr)
            return 1
    return repl()


if __name__ == "__main__":
    raise SystemExit(main())
