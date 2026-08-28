"""Interpreter (evaluator) for செயல்மொழி (Seyal Mozhi)."""

import importlib

from . import ast_nodes as A


class SeyalRuntimeError(Exception):
    def __init__(self, msg, line=None):
        loc = f"வரி {line}: " if line is not None else ""
        super().__init__(loc + msg)
        self.line = line


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name, line=None):
        env = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise SeyalRuntimeError(f"'{name}' எனும் பெயர் அறியப்படவில்லை (undefined name)", line)

    def set_existing(self, name, value):
        env = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return True
            env = env.parent
        return False

    def declare(self, name, value):
        self.vars[name] = value


class SeyalFunction:
    def __init__(self, name, params, body, closure_env, interp):
        self.name = name
        self.params = params
        self.body = body
        self.closure_env = closure_env
        self.interp = interp

    def __call__(self, *args):
        if len(args) != len(self.params):
            raise SeyalRuntimeError(
                f"'{self.name}' செயலுக்கு {len(self.params)} அளவுருக்கள் தேவை, "
                f"{len(args)} கொடுக்கப்பட்டது (wrong number of arguments)"
            )
        local_env = Environment(parent=self.closure_env)
        for p, a in zip(self.params, args):
            local_env.declare(p, a)
        try:
            self.interp.exec_block(self.body, local_env)
        except ReturnSignal as r:
            return r.value
        return None


def _tamil_str(value):
    if value is True:
        return "உண்மை"
    if value is False:
        return "பொய்"
    if value is None:
        return "வெறுமை"
    if isinstance(value, list):
        return "[" + ", ".join(_tamil_str(v) for v in value) + "]"
    return str(value)


def _truthy(value):
    return bool(value)


class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self._install_builtins()

    def _install_builtins(self):
        g = self.globals
        g.declare("நீளம்", lambda x: len(x))                    # length
        g.declare("வரம்பு", lambda *a: list(range(*a)))          # range
        g.declare("எண்ணாக்கு", lambda x: int(x))                 # to int
        g.declare("தசமமாக்கு", lambda x: float(x))               # to float
        g.declare("சரமாக்கு", lambda x: _tamil_str(x))           # to string
        g.declare("உள்ளீடு", lambda *a: input(*a))               # input
        g.declare("சேர்", self._builtin_append)                  # list.append
        g.declare("நீக்கு", self._builtin_remove)                 # list.remove/pop
        g.declare("வரிசைப்படுத்து", lambda lst: sorted(lst))      # sort
        g.declare("கூட்டு", lambda a, b: a + b)                  # sum two / concat
        g.declare("அதிகபட்சம்", lambda *a: max(*a) if len(a) > 1 else max(a[0]))
        g.declare("குறைந்தபட்சம்", lambda *a: min(*a) if len(a) > 1 else min(a[0]))
        g.declare("முழுமையாக", lambda x: abs(x))                 # abs
        g.declare("வகை", lambda x: type(x).__name__)             # type

    @staticmethod
    def _builtin_append(lst, value):
        lst.append(value)
        return lst

    @staticmethod
    def _builtin_remove(lst, index=None):
        if index is None:
            return lst.pop()
        return lst.pop(index)

    # ---- running programs ----
    def run(self, source, filename="<program>"):
        from .lexer import tokenize
        from .parser import parse
        tokens = tokenize(source)
        tree = parse(tokens)
        self.exec_block(tree.statements, self.globals)

    def exec_block(self, statements, env):
        for stmt in statements:
            self.exec_stmt(stmt, env)

    # ---- statements ----
    def exec_stmt(self, stmt, env):
        method = getattr(self, f"exec_{type(stmt).__name__}", None)
        if method is None:
            raise SeyalRuntimeError(f"தெரியாத கட்டளை வகை {type(stmt).__name__}")
        method(stmt, env)

    def exec_LetStmt(self, stmt, env):
        value = self.eval(stmt.expr, env)
        env.declare(stmt.name, value)

    def exec_AssignStmt(self, stmt, env):
        value = self.eval(stmt.expr, env)
        target = stmt.target
        if isinstance(target, A.Ident):
            if not env.set_existing(target.name, value):
                # implicit declare on first assignment for convenience
                env.declare(target.name, value)
        elif isinstance(target, A.Index):
            obj = self.eval(target.obj, env)
            idx = self.eval(target.index, env)
            obj[idx] = value
        elif isinstance(target, A.Attr):
            obj = self.eval(target.obj, env)
            setattr(obj, target.name, value)
        else:
            raise SeyalRuntimeError("இதற்கு மதிப்பை வைக்க முடியாது (invalid assignment target)", stmt.line)

    def exec_PrintStmt(self, stmt, env):
        values = [self.eval(a, env) for a in stmt.args]
        print(" ".join(_tamil_str(v) for v in values))

    def exec_IfStmt(self, stmt, env):
        for cond, body in stmt.branches:
            if _truthy(self.eval(cond, env)):
                self.exec_block(body, Environment(parent=env))
                return
        if stmt.else_body is not None:
            self.exec_block(stmt.else_body, Environment(parent=env))

    def exec_WhileStmt(self, stmt, env):
        while _truthy(self.eval(stmt.cond, env)):
            try:
                self.exec_block(stmt.body, Environment(parent=env))
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def exec_ForStmt(self, stmt, env):
        iterable = self.eval(stmt.iterable, env)
        for item in iterable:
            loop_env = Environment(parent=env)
            loop_env.declare(stmt.var_name, item)
            try:
                self.exec_block(stmt.body, loop_env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def exec_FuncDef(self, stmt, env):
        fn = SeyalFunction(stmt.name, stmt.params, stmt.body, env, self)
        env.declare(stmt.name, fn)

    def exec_ReturnStmt(self, stmt, env):
        value = self.eval(stmt.expr, env) if stmt.expr is not None else None
        raise ReturnSignal(value)

    def exec_BreakStmt(self, stmt, env):
        raise BreakSignal()

    def exec_ContinueStmt(self, stmt, env):
        raise ContinueSignal()

    def exec_ImportStmt(self, stmt, env):
        try:
            module = importlib.import_module(stmt.module_name)
        except ImportError as e:
            raise SeyalRuntimeError(
                f"'{stmt.module_name}' எனும் நூலகத்தை இறக்குமதி செய்ய முடியவில்லை (cannot import module): {e}",
                stmt.line,
            )
        name = stmt.alias or stmt.module_name
        env.declare(name, module)

    def exec_ExprStmt(self, stmt, env):
        self.eval(stmt.expr, env)

    # ---- expressions ----
    def eval(self, node, env):
        method = getattr(self, f"eval_{type(node).__name__}", None)
        if method is None:
            raise SeyalRuntimeError(f"தெரியாத வெளிப்பாடு வகை {type(node).__name__}")
        return method(node, env)

    def eval_Number(self, node, env):
        return node.value

    def eval_String(self, node, env):
        return node.value

    def eval_Bool(self, node, env):
        return node.value

    def eval_NoneLit(self, node, env):
        return None

    def eval_Ident(self, node, env):
        return env.get(node.name, node.line)

    def eval_ListLit(self, node, env):
        return [self.eval(i, env) for i in node.items]

    def eval_Index(self, node, env):
        obj = self.eval(node.obj, env)
        idx = self.eval(node.index, env)
        try:
            return obj[idx]
        except (IndexError, KeyError) as e:
            raise SeyalRuntimeError(f"குறியீடு எல்லை தாண்டியது (index error): {e}", node.line)

    def eval_Attr(self, node, env):
        obj = self.eval(node.obj, env)
        try:
            return getattr(obj, node.name)
        except AttributeError as e:
            raise SeyalRuntimeError(f"பண்பு இல்லை (no such attribute): {e}", node.line)

    def eval_UnaryOp(self, node, env):
        val = self.eval(node.operand, env)
        if node.op == "MINUS":
            return -val
        if node.op == "PLUS":
            return +val
        if node.op == "NOT":
            return not _truthy(val)
        raise SeyalRuntimeError(f"தெரியாத ஒற்றை செயலி {node.op}", node.line)

    def eval_BinOp(self, node, env):
        if node.op == "AND":
            left = self.eval(node.left, env)
            if not _truthy(left):
                return left
            return self.eval(node.right, env)
        if node.op == "OR":
            left = self.eval(node.left, env)
            if _truthy(left):
                return left
            return self.eval(node.right, env)

        left = self.eval(node.left, env)
        right = self.eval(node.right, env)
        op = node.op
        try:
            if op == "PLUS":
                return left + right
            if op == "MINUS":
                return left - right
            if op == "STAR":
                return left * right
            if op == "SLASH":
                return left / right
            if op == "FLOORDIV":
                return left // right
            if op == "PERCENT":
                return left % right
            if op == "POW":
                return left ** right
            if op == "EQ":
                return left == right
            if op == "NEQ":
                return left != right
            if op == "LT":
                return left < right
            if op == "GT":
                return left > right
            if op == "LE":
                return left <= right
            if op == "GE":
                return left >= right
        except TypeError as e:
            raise SeyalRuntimeError(f"வகைப் பிழை (type error): {e}", node.line)
        except ZeroDivisionError:
            raise SeyalRuntimeError("பூஜ்ஜியத்தால் வகுக்க முடியாது (division by zero)", node.line)
        raise SeyalRuntimeError(f"தெரியாத செயலி {op}", node.line)

    def eval_Call(self, node, env):
        callee = self.eval(node.callee, env)
        args = [self.eval(a, env) for a in node.args]
        if not callable(callee):
            raise SeyalRuntimeError(f"இது ஒரு செயல் அல்ல, அழைக்க முடியாது (not callable)", node.line)
        try:
            return callee(*args)
        except SeyalRuntimeError:
            raise
        except (ReturnSignal, BreakSignal, ContinueSignal):
            raise
        except Exception as e:
            raise SeyalRuntimeError(f"செயல் அழைப்பில் பிழை (error calling function): {e}", node.line)
