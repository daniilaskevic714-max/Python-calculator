"""Точка входа для ``python -m calculator`` (по умолчанию — консольный режим)."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
