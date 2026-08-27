"""Пакет «Мини-калькулятор»: ядро вычислений и два интерфейса (GUI, CLI)."""

from .core import CalculatorError, calculate, evaluate, format_result

__all__ = ["CalculatorError", "calculate", "evaluate", "format_result"]
__version__ = "1.0.0"
