import ast
import operator
from flask import Flask, request, jsonify

app = Flask(__name__)

# Allowed operators
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

# Guard against resource-exhaustion via huge exponents like 9**9**9
_MAX_POW_EXPONENT = 1000


def _eval(node):
    if isinstance(node, ast.Constant):  # numbers only
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    elif isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left = _eval(node.left)
        right = _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POW_EXPONENT:
            raise ValueError("Exponent too large")
        return _BIN_OPS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    else:
        raise ValueError("Unsupported expression")


def safe_eval(expr: str):
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
