import ast
import operator
from flask import Flask, request, jsonify

app = Flask(__name__)

# Allowed operators mapped to their safe implementations
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


def safe_eval(expr):
    """Safely evaluate a math expression, allowing only arithmetic."""
    def _eval(node):
        if isinstance(node, ast.Constant):  # numbers
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numeric constants are allowed")
        if isinstance(node, ast.BinOp):
            op = _BIN_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Operator {type(node.op).__name__} not allowed")
            return op(_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op = _UNARY_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Operator {type(node.op).__name__} not allowed")
            return op(_eval(node.operand))
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

    tree = ast.parse(expr, mode="eval")
    return _eval(tree.body)


@app.route("/calc")
def calc():
    expr = request.args.get("expr", "")
    if not expr:
        return jsonify(error="Missing 'expr' query parameter"), 400
    try:
        result = safe_eval(expr)
    except ZeroDivisionError:
        return jsonify(error="Division by zero"), 400
    except (ValueError, SyntaxError, TypeError) as e:
        return jsonify(error=f"Invalid expression: {e}"), 400
    return jsonify(expr=expr, result=result)


if __name__ == "__main__":
    app.run(debug=True)
