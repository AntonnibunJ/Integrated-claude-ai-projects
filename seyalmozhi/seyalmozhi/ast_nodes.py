"""AST node types for செயல்மொழி (Seyal Mozhi)."""


class Node:
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{self.__class__.__name__}({fields})"


class Program(Node):
    def __init__(self, statements):
        self.statements = statements


# ---- Statements ----

class LetStmt(Node):
    def __init__(self, name, expr, line):
        self.name = name
        self.expr = expr
        self.line = line


class AssignStmt(Node):
    def __init__(self, target, expr, line):
        self.target = target  # Ident or Index node
        self.expr = expr
        self.line = line


class PrintStmt(Node):
    def __init__(self, args, line):
        self.args = args
        self.line = line


class IfStmt(Node):
    def __init__(self, branches, else_body, line):
        # branches: list of (condition_expr, body_statements)
        self.branches = branches
        self.else_body = else_body
        self.line = line


class WhileStmt(Node):
    def __init__(self, cond, body, line):
        self.cond = cond
        self.body = body
        self.line = line


class ForStmt(Node):
    def __init__(self, var_name, iterable, body, line):
        self.var_name = var_name
        self.iterable = iterable
        self.body = body
        self.line = line


class FuncDef(Node):
    def __init__(self, name, params, body, line):
        self.name = name
        self.params = params
        self.body = body
        self.line = line


class ReturnStmt(Node):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line


class BreakStmt(Node):
    def __init__(self, line):
        self.line = line


class ContinueStmt(Node):
    def __init__(self, line):
        self.line = line


class ImportStmt(Node):
    def __init__(self, module_name, alias, line):
        self.module_name = module_name
        self.alias = alias
        self.line = line


class ExprStmt(Node):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line


# ---- Expressions ----

class Number(Node):
    def __init__(self, value):
        self.value = value


class String(Node):
    def __init__(self, value):
        self.value = value


class Bool(Node):
    def __init__(self, value):
        self.value = value


class NoneLit(Node):
    pass


class Ident(Node):
    def __init__(self, name, line):
        self.name = name
        self.line = line


class ListLit(Node):
    def __init__(self, items):
        self.items = items


class Index(Node):
    def __init__(self, obj, index, line):
        self.obj = obj
        self.index = index
        self.line = line


class Attr(Node):
    def __init__(self, obj, name, line):
        self.obj = obj
        self.name = name
        self.line = line


class BinOp(Node):
    def __init__(self, op, left, right, line):
        self.op = op
        self.left = left
        self.right = right
        self.line = line


class UnaryOp(Node):
    def __init__(self, op, operand, line):
        self.op = op
        self.operand = operand
        self.line = line


class Call(Node):
    def __init__(self, callee, args, line):
        self.callee = callee
        self.args = args
        self.line = line
