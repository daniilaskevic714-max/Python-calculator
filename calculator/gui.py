"""Графический интерфейс калькулятора на tkinter.

Запуск:  python gui.py    (из папки проекта)  или  python -m calculator.gui
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from .core import CalculatorError, calculate

_KEYS = (
    ("7", "8", "9", "÷"),
    ("4", "5", "6", "×"),
    ("1", "2", "3", "−"),
    ("0", ".", "(", ")"),
    ("C", "⌫", "+", "="),
)

_DIGIT_BG = "#f4f6fb"
_OP_BG = "#dde3f0"
_EQ_BG = "#4f6bed"
_SPECIAL_BG = "#f6d7d7"


class CalculatorApp(tk.Tk):
    def __init__(self) -> None:  # noqa: D107 - tkinter-идиома
        super().__init__()
        self.title("Мини-калькулятор")
        self.resizable(False, False)
        self.configure(bg="#ffffff", padx=12, pady=12)

        self.expression = tk.StringVar(value="")
        self._build_display()
        self._build_keys()
        self._bind_keys()

    # --- виджеты ---------------------------------------------------------
    def _build_display(self) -> None:
        frame = tk.Frame(self, bg="#ffffff")
        frame.pack(fill="x", pady=(0, 10))

        self.entry = tk.Entry(
            frame,
            textvariable=self.expression,
            font=tkfont.Font(family="DejaVu Sans", size=22, weight="bold"),
            justify="right",
            bd=0,
            bg="#eef1f8",
            insertbackground="#1a1a1a",
            highlightthickness=1,
            highlightbackground="#c9d2e6",
            highlightcolor="#4f6bed",
        )
        self.entry.grid(row=0, column=0, sticky="nsew", ipady=14, padx=(0, 6))
        self.entry.icursor(tk.END)

        tk.Button(
            frame,
            text="⧉",
            width=3,
            bd=0,
            bg="#eef1f8",
            activebackground="#dde3f0",
            command=self.copy_result,
        ).grid(row=0, column=1, sticky="ns")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.status = tk.Label(
            self, text="готово", anchor="e", bd=0, bg="#ffffff", fg="#7a8194", font=("DejaVu Sans", 9)
        )
        self.status.pack(fill="x", pady=(0, 6))

    def _build_keys(self) -> None:
        grid = tk.Frame(self, bg="#ffffff")
        grid.pack(fill="both", expand=True)

        for row, labels in enumerate(_KEYS):
            grid.columnconfigure(row, weight=1, uniform="key")
            grid.rowconfigure(row, weight=1, uniform="key")
            for col, label in enumerate(labels):
                grid.columnconfigure(col, weight=1, uniform="key")
                text, action = self._action_for(label)
                bg = {
                    "digit": _DIGIT_BG,
                    "op": _OP_BG,
                    "eq": _EQ_BG,
                    "special": _SPECIAL_BG,
                }[action[0]]
                tk.Button(
                    grid,
                    text=text,
                    font=("DejaVu Sans", 15, "bold"),
                    bd=0,
                    bg=bg,
                    activebackground="#c9d2e6",
                    fg="#10131a" if action[0] != "eq" else "#ffffff",
                    takefocus=0,
                    command=lambda a=action: self.press(a),
                ).grid(row=row, column=col, sticky="nsew", padx=3, pady=3)

    def _bind_keys(self) -> None:
        self.bind("<Return>", lambda _e: self.press(("eq", "=")))
        self.bind("<KP_Enter>", lambda _e: self.press(("eq", "=")))
        self.bind("<Escape>", lambda _e: self.press(("special", "AC")))

    # --- логика ---------------------------------------------------------
    @staticmethod
    def _action_for(label: str) -> tuple[str, str]:
        if label == "=":
            return ("eq", "=")
        if label == "C":
            return ("special", "AC")
        if label == "⌫":
            return ("special", "DEL")
        return ("insert", {"÷": "/", "×": "*", "−": "-", "+": "+"}.get(label, label))

    def press(self, action: tuple[str, str]) -> None:
        """Один «клик»: вставить символ, стереть, очистить или вычислить."""
        kind, payload = action
        current = self.expression.get()
        if kind == "insert":
            self.expression.set(current + payload)
        elif payload == "AC":
            self.expression.set("")
            self.set_status("готово")
        elif payload == "DEL":
            self.expression.set(current[:-1])
            self.set_status("готово")
        else:
            self.calculate()
        self.entry.icursor(tk.END)

    def calculate(self) -> None:
        try:
            result = calculate(self.expression.get())
        except CalculatorError as exc:
            self.set_status(f"ошибка: {exc}")
            self.entry.bell()
            return
        self.expression.set(result)
        self.set_status(f"= {result}  (⧉ — скопировать)")

    def copy_result(self) -> None:
        try:
            self.clipboard_clear()
            self.clipboard_append(self.expression.get())
            self.set_status("скопировано в буфер обмена")
        except tk.TclError:
            self.set_status("буфер обмена недоступен")

    def set_status(self, text: str) -> None:
        self.status.config(text=text)


def run() -> int:
    try:
        app = CalculatorApp()
    except tk.TclError as exc:  # нет X11/Wayland (например, чистый WSL или CI)
        print(f"Не удалось открыть окно: {exc}\nИспользуйте консольный режим: python -m calculator")
        return 1
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
