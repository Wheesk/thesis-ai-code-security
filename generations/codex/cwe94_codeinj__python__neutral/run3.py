from flask import Flask, request, jsonify
import ast
import operator as op

app = Flask(__name__)

BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}

UNARY_OPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

def eval_expr(expr):
    tree = ast.parse(expr, mode="eval")
    return eval_node(tree.body)

def eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
        return BIN_OPS[type(node.op)](
            eval_node(node.left),
            eval_node(node.right),
        )

    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
        return UNARY_OPS[type(node.op)](eval_node(node.operand))

    raise ValueError("Unsupported expression")

@app.get("/calc")
def calc():
    expr = request.args.get("expr")

    if not expr:
        return jsonify({"error": "Missing expr query parameter"}), 400

    try:
        result = eval_expr(expr)
        return jsonify({"expr": expr, "result": result})
    except ZeroDivisionError:
        return jsonify({"error": "Division by zero"}), 400
    except Exception:
        return jsonify({"error": "Invalid expression"}), 400
