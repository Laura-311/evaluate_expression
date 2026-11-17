import sys


class Stack:
    """A simple stack (LIFO) backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}


def apply_operator(operator, left, right):
    """Apply a binary operator to two operands."""
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        return left / right
    raise ValueError(f"unknown operator '{operator}'")


def tokenize(expression):
    """Split an expression string into numbers, operators and parentheses.

    A '-' is treated as a unary minus (part of the number) when it appears at
    the start, after '(' or after another operator, e.g. '-5 + 3' or '2 * -3'.
    """
    tokens = []
    i = 0
    n = len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            start = i
            while i < n and (expression[i].isdigit() or expression[i] == "."):
                i += 1
            text = expression[start:i]
            try:
                tokens.append(float(text))
            except ValueError:
                raise ValueError(f"invalid number '{text}'")
        elif ch in "+-*/()":
            is_unary = ch == "-" and (
                not tokens or tokens[-1] in ("(", "+", "-", "*", "/")
            )
            if is_unary:
                # Represent unary minus as (0 - ...) handled via a marker token
                tokens.append("u-")
            else:
                tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"invalid character '{ch}'")
    return tokens


def evaluate_expression(expression):
    """Evaluate an infix expression using an operand stack and operator stack.

    Supports + - * /, parentheses, decimals, unary minus and precedence rules.
    Returns an int when the result is whole, otherwise a float.
    """
    tokens = tokenize(expression)
    if not tokens:
        raise ValueError("empty expression")

    values = Stack()      # operands
    operators = Stack()   # operators and '('

    def reduce_once():
        op = operators.pop()
        if op == "u-":
            values.push(-values.pop())
        else:
            right = values.pop()
            left = values.pop()
            values.push(apply_operator(op, left, right))

    try:
        for token in tokens:
            if isinstance(token, float):
                values.push(token)
            elif token == "(":
                operators.push(token)
            elif token == ")":
                while not operators.is_empty() and operators.peek() != "(":
                    reduce_once()
                if operators.is_empty():
                    raise ValueError("mismatched parentheses")
                operators.pop()  # discard '('
            elif token == "u-":
                operators.push(token)  # unary minus binds tightest
            else:
                while (
                    not operators.is_empty()
                    and operators.peek() != "("
                    and (
                        operators.peek() == "u-"
                        or PRECEDENCE[operators.peek()] >= PRECEDENCE[token]
                    )
                ):
                    reduce_once()
                operators.push(token)

        while not operators.is_empty():
            if operators.peek() == "(":
                raise ValueError("mismatched parentheses")
            reduce_once()

        result = values.pop()
        if not values.is_empty():
            raise ValueError("malformed expression")
    except IndexError:
        raise ValueError("malformed expression")

    if result == int(result):
        return int(result)
    return round(result, 6)


def is_separator(line):
    """A separator line contains only dashes (e.g. '-----')."""
    stripped = line.strip()
    return len(stripped) >= 2 and set(stripped) == {"-"}


def process_file(input_path, output_path):
    """Read expressions, evaluate each, write results in the same format."""
    with open(input_path, "r") as infile:
        lines = infile.read().splitlines()

    output_lines = []
    for line in lines:
        if is_separator(line):
            output_lines.append(line.strip())   # keep the same separator
        elif line.strip() == "":
            continue                             # ignore blank lines
        else:
            try:
                output_lines.append(str(evaluate_expression(line)))
            except ZeroDivisionError:
                output_lines.append("Error: division by zero")
            except ValueError as err:
                output_lines.append(f"Error: {err}")

    with open(output_path, "w") as outfile:
        outfile.write("\n".join(output_lines) + "\n")


if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    try:
        process_file(in_file, out_file)
        print(f"Results written to {out_file}")
    except FileNotFoundError:
        print(f"Error: could not find '{in_file}'")
