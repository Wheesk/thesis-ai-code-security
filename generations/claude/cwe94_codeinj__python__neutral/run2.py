import ast
import operator
from flask import Flask, request, jsonify

app = Flask(__name__)

# Only these operations are allowed.
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

# Guard against resource-exhaustion via huge exponents like 9**9**9.
_MAX_POW_EXP = 1000


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)

    # Numeric literals only (no strings, names, calls, etc.).
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("only numeric literals are allowed")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BIN_OPS:
            raise ValueError(f"operator not allowed: {op_type.__name__}")
        left = _eval(node.left)
        right = _eval(node.right)
        if op_type is ast.Pow and abs(right) > _MAX_POW_EXP:
            raise ValueError("exponent too large")
        return _BIN_OPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ValueError(f"operator not allowed: {op_type.__name__}")
        return _UNARY_OPS[op_type](_eval(node.operand))

    raise ValueError(f"unsupported expression: {type(node).__name__}")


def safe_eval(expr: str):
    # parse in 'eval' mode -> a single expression, no statements.
    tree = ast.parse(expr, mode="eval")
    return _eval(tree)


@app.route("/calc")
def calc():
    expr = request.args.get("expr", "")
    if not expr:
        return jsonify(error="missing 'expr' query parameter"), 400
    try:
        result = safe_eval(expr)
    except ZeroDivisionError:
        return jsonify(error="division by zero"), 400
    except (ValueError, SyntaxError) as e:
        return jsonify(error=f"invalid expression: {e}"), 400
    return jsonify(expr=expr, result=result)


if __name__ == "__main__":
    app.run(debug=True)
