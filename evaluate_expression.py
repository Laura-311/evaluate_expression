class Stack:
    """A custom Stack class supporting push, pop, peek, is_empty, and size operations."""

    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("pop from empty stack")

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("peek from empty stack")

    def size(self):
        return len(self.items)


def precedence(op):
    """Returns the precedence of mathematical operators."""
    if op in ('+', '-'):
        return 1
    if op in ('*', '/'):
        return 2
    return 0


def apply_op(a, b, op):
    """Applies an operator to two operands."""
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a / b


def evaluate_expression(expression):
    """Evaluates an infix mathematical expression using a stack-based approach."""
    import re
    tokens = re.findall(r'\d+\.?\d*|\+|\-|\*|\/|\(|\)', expression)

    values = Stack()
    ops = Stack()

    i = 0
    while i < len(tokens):
        token = tokens[i]

        # If token is a number, push it to the values stack
        if token.replace('.', '', 1).isdigit():
            values.push(float(token) if '.' in token else int(token))

        # If token is an opening parenthesis, push to ops stack
        elif token == '(':
            ops.push(token)

        # If token is a closing parenthesis, solve entire parenthesis
        elif token == ')':
            while not ops.is_empty() and ops.peek() != '(':
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.push(apply_op(val1, val2, op))
            if not ops.is_empty() and ops.peek() == '(':
                ops.pop()

        # If token is an operator
        elif token in '+-*/':
            while (not ops.is_empty() and
                   precedence(ops.peek()) >= precedence(token) and
                   ops.peek() != '('):
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.push(apply_op(val1, val2, op))
            ops.push(token)

        i += 1

    # Apply remaining operations in the stacks
    while not ops.is_empty():
        val2 = values.pop()
        val1 = values.pop()
        op = ops.pop()
        values.push(apply_op(val1, val2, op))

    return values.pop()


def process_expressions(input_filename="input.txt", output_filename="output.txt"):
    """Reads expressions separated by separator lines from input.txt and writes results to output.txt."""
    try:
        with open(input_filename, 'r') as infile:
            content = infile.read()

        # Split input content into blocks based on lines containing separators (e.g., -----)
        lines = content.split('\n')
        expressions = []
        current_expr_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Check if line is a separator (consisting entirely of hyphens)
            if all(char == '-' for char in stripped):
                if current_expr_lines:
                    expressions.append(" ".join(current_expr_lines))
                    current_expr_lines = []
            else:
                current_expr_lines.append(stripped)

        if current_expr_lines:
            expressions.append(" ".join(current_expr_lines))

        # Evaluate each expression and store results
        results = []
        for expr in expressions:
            if not expr.strip():
                continue
            try:
                result = evaluate_expression(expr)
                results.append(f"{expr} = {result}")
            except Exception as e:
                results.append(f"{expr} = Error: {str(e)}")

        # Write results to output file
        with open(output_filename, 'w') as outfile:
            outfile.write("\n".join(results) + "\n")

        print(f"Successfully evaluated {len(results)} expressions. Results written to {output_filename}.")

    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")


if __name__ == "__main__":
    process_expressions()