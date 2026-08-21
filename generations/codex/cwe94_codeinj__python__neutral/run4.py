from flask import Flask, request, jsonify
import ast
import operator as op

app = Flask(__name__)

OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def eval_expr(expr):
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Invalid expression")

    tree = ast.parse(expr, mode="eval")
    return _eval(tree)

@app.get("/calc")
def calc():
    expr = request.args.get("expr")

    if not expr:
        return jsonify({"error": "Missing expr query parameter"}), 400

    try:
        result = eval_expr(expr)
        return jsonify({"expr": expr, "result": result})
    except Exception:
        return jsonify({"error": "Invalid expression"}), 400
