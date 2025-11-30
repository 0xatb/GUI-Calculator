# calculator.py
import tkinter as tk
from tkinter import font
import ast
import operator as op

# -------------------------
# Safe expression evaluator
# -------------------------
# Only allow a small set of arithmetic operations.
_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def safe_eval(expr: str):
    """
    Safely evaluate a math expression using ast parsing.
    Supports + - * / % ** unary +/-, parentheses, integers and floats.
    Raises ValueError for invalid syntax or unsupported nodes.
    """
    # Replace caret ^ with pow operator (user-friendly)
    expr = expr.replace('^', '**')
    try:
        node = ast.parse(expr, mode='eval')
    except SyntaxError as e:
        raise ValueError("Syntax error") from e

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in _ALLOWED_OPERATORS:
                return _ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type}")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in _ALLOWED_OPERATORS:
                return _ALLOWED_OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type}")
        if isinstance(node, ast.Num):  # Python <3.8
            return node.n
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Constants other than numbers not allowed")
        if isinstance(node, ast.Call):
            raise ValueError("Function calls not allowed")
        raise ValueError(f"Unsupported expression: {type(node)}")

    result = _eval(node)
    # Convert results like 5.0 -> 5 for nicer display
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result

# -------------------------
# GUI
# -------------------------
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.configure(padx=10, pady=10, bg="#f0f0f0")

        # fonts
        self.display_font = font.Font(size=20, weight="bold")
        self.button_font = font.Font(size=14)

        # state
        self._expr = tk.StringVar(value="")

        # display
        self._create_display()

        # buttons
        self._create_buttons()

        # keyboard bindings
        self._bind_keys()

    def _create_display(self):
        # Entry-like read-only display
        disp = tk.Entry(self, textvariable=self._expr, justify='right',
                        font=self.display_font, bd=4, relief='ridge', width=18)
        disp.grid(row=0, column=0, columnspan=4, pady=(0,10))
        disp.configure(state='readonly')

    def _create_buttons(self):
        btns = [
            ('C', 1, 0, self.clear),
            ('⌫', 1, 1, self.backspace),
            ('%', 1, 2, lambda: self._append('%')),
            ('/', 1, 3, lambda: self._append('/')),

            ('7', 2, 0, lambda: self._append('7')),
            ('8', 2, 1, lambda: self._append('8')),
            ('9', 2, 2, lambda: self._append('9')),
            ('*', 2, 3, lambda: self._append('*')),

            ('4', 3, 0, lambda: self._append('4')),
            ('5', 3, 1, lambda: self._append('5')),
            ('6', 3, 2, lambda: self._append('6')),
            ('-', 3, 3, lambda: self._append('-')),

            ('1', 4, 0, lambda: self._append('1')),
            ('2', 4, 1, lambda: self._append('2')),
            ('3', 4, 2, lambda: self._append('3')),
            ('+', 4, 3, lambda: self._append('+')),

            ('(', 5, 0, lambda: self._append('(')),
            ('0', 5, 1, lambda: self._append('0')),
            ('.', 5, 2, lambda: self._append('.')),
            (')', 5, 3, lambda: self._append(')')),

            ('^', 6, 0, lambda: self._append('^')),
            ('=', 6, 1, self.evaluate, 3),  # '=' spans 3 columns
        ]

        for (text, r, c, cmd, colspan) in [(t,r,c,cb,1) if len(tpl:=t) else None for t,r,c,cb,*rest in btns]:
            pass  # keep structure for readability

        # build buttons (explicit loop for colspan handling)
        for item in btns:
            text, r, c, cmd = item[0], item[1], item[2], item[3]
            colspan = item[4] if len(item) > 4 else 1
            b = tk.Button(self, text=text, width=5, height=2, font=self.button_font,
                          command=cmd, relief='raised')
            b.grid(row=r, column=c, columnspan=colspan, sticky='nsew', padx=3, pady=3)

        # make columns expand equally (keeps buttons square-ish)
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

    # helpers
    def _append(self, char):
        cur = self._expr.get()
        self._expr.set(cur + char)

    def clear(self):
        self._expr.set("")

    def backspace(self):
        cur = self._expr.get()
        self._expr.set(cur[:-1])

    def evaluate(self, _event=None):
        expr = self._expr.get().strip()
        if not expr:
            return
        try:
            res = safe_eval(expr)
            self._expr.set(str(res))
        except Exception as e:
            self._expr.set("Error")

    # keyboard
    def _bind_keys(self):
        # numeric keys, operators, parentheses, dot
        for key in '0123456789+-*/().%^':
            # use lambda with default to capture current key
            self.bind(key, lambda ev, k=key: self._append(k))
        # Enter to evaluate
        self.bind('<Return>', self.evaluate)
        self.bind('<KP_Enter>', self.evaluate)
        # Backspace and Delete
        self.bind('<BackSpace>', lambda ev: self.backspace())
        self.bind('<Delete>', lambda ev: self.clear())
        # Allow uppercase ^ from Shift+6 is handled as '^' already

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()

