from flask import Flask, jsonify, request
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
    def walk(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](walk(node.left), walk(node.right))

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](walk(node.operand))

        raise ValueError("unsupported expression")

    return walk(ast.parse(expr, mode="eval").body)


@app.get("/calc")
def calc():
    expr = request.args.get("expr")

    if not expr:
        return jsonify(error="missing expr"), 400

    try:
        return jsonify(result=eval_expr(expr))
    except Exception as exc:
        return jsonify(error=str(exc)), 400
