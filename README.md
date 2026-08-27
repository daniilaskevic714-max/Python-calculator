# Мини-калькулятор на Python

Минимальный, но «взрослый» калькулятор: одно ядро вычислений, два интерфейса —
**GUI на tkinter** и **CLI в терминале**. Без внешних зависимостей, только стандартная библиотека.

```
.
├── gui.py               # запуск окна:  python gui.py
├── calculator/
│   ├── __init__.py      # публичный API пакета
│   ├── __main__.py      # запуск консоли:  python -m calculator
│   ├── core.py          # ядро: безопасный парсер + Decimal-арифметика
│   ├── cli.py           # интерфейс командной строки (REPL)
│   └── gui.py           # интерфейс tkinter
├── tests/
│   └── test_core.py     # 19 тестов ядра
├── pyproject.toml
├── requirements.txt     # пусто: зависимостей нет
└── README.md
```

## Скачать одним архивом

Архив не лежит в дереве репозитория — он published как ассет в
**[Releases](https://github.com/daniilaskevic714-max/Python-calculator/releases/latest)**:

| Файл                          | Что внутри                                              |
|-------------------------------|---------------------------------------------------------|
| `Python-calculator-<версия>.zip` | снимок исходников этого тега, всё в папке `Python-calculator/` |
| `SHA256SUMS.txt`              | контрольная сумма архива                                |

Содержимое — дерево релизного тега, собранные `git archive`; `.git`, кэши и
сам архив в него не попадают:

```bash
git archive --format=zip --prefix=Python-calculator/ \
    -o Python-calculator-1.0.0.zip v1.0.0
```

Скачанный архив можно запускать сразу — зависимостей нет:

```bash
curl -sLO https://github.com/daniilaskevic714-max/Python-calculator/releases/latest/download/Python-calculator-1.0.0.zip
curl -sLO https://github.com/daniilaskevic714-max/Python-calculator/releases/latest/download/SHA256SUMS.txt
sha256sum -c SHA256SUMS.txt                  # на macOS: shasum -a 256 -c
unzip Python-calculator-1.0.0.zip && cd Python-calculator
python gui.py                             # окно
python -m calculator "2+3*4"              # 14
python -m unittest discover -s tests -t . # 19 tests, OK
```

## Быстрый старт

```bash
python gui.py                # окно-калькулятор
python -m calculator         # режим REPL в терминале
python -m calculator "2+3*4" # разовый расчёт -> 14
```

Python **3.10+** (используется `match`). GUI требует `tkinter` — он входит в стандартную
сборку Python на Windows и macOS; на Debian/Ubuntu ставится отдельно:

```bash
sudo apt install python3-tk
```

## Что умеет

| Возможность        | Пример ввода              | Результат        |
|--------------------|---------------------------|------------------|
| Приоритет операций | `2 + 3 * 4`               | `14`             |
| Скобки             | `(2 + 3) * 4`             | `20`             |
| Целочисленное деление, остаток | `7 // 2`, `7 % 3` | `3`, `1`   |
| Степень            | `2^10` или `2 ** 10`      | `1024`           |
| Точные дроби       | `0.1 + 0.2`               | `0.3`            |
| Константы          | `pi * 2`                  | `6.28318530718`  |
| Запятая как разделитель | `2,5 + 1`            | `3.5`            |
| «Человеческие» значки | `6 × 7 ÷ 2`           | `21`             |
| Очень большие числа | `10^400`                  | `1e+400`         |

В REPL дополнительно: `ans` (предыдущий результат), `history`, `clear`, `help`, `exit`.

## Почему это не `eval(input())`

`calculator/core.py` разбирает строку через `ast.parse` и вычисляет **только** побитово
разрешённые узлы: числа, скобки и операции `+ - * / // % **`. Все остальное —
`NameError`, вызовы, индексы, списки, `import` — отклоняется с `CalculatorError`.
Дополнительно ограничены длина выражения (200 символов) и порядок степени,
чтобы `2 ^ 10^2000` не подвешивал процесс.

## Числа: `Decimal`, а не `float`

Вычисления идут в `decimal.Decimal` с точностью 28 знаков, а на экран выводится
12 значащих цифр. Поэтому `0.1 + 0.2` даёт `0.3`, а не `0.30000000000000004`.

## Клавиатура в GUI

- `0-9 . ( ) + - * /` — ввод,
- `Enter` — вычислить,
- `Backspace` — стереть символ, `Esc` — очистить всё,
- кнопка `⧉` — скопировать результат в буфер обмена.

## Тесты

```bash
python -m unittest discover -s tests -t . -v   # 19 tests, OK
# или, если установлен pytest:
python -m pytest -q
```

## Структура кода

- `evaluate(expr) -> Decimal` — «строка → число»;
- `format_result(value) -> str` — «число → аккуратная строка»;
- `calculate(expr) -> str` — то же самое одной функцией, именно её зовут GUI и CLI.

Чтобы добавить свою обвязку (бот, телеграм, веб-API), достаточно импортировать `calculate`:

```python
from calculator import evaluate          # или from calculator.core import calculate
```

## Лицензия

MIT — см. [LICENSE](LICENSE).
