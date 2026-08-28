"""Parser for செயல்மொழி (Seyal Mozhi). Builds an AST from tokens."""

from . import ast_nodes as A


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---- token helpers ----
    def peek(self, offset=0):
        return self.tokens[self.pos + offset]

    def at(self, *types):
        return self.peek().type in types

    def advance(self):
        tok = self.tokens[self.pos]
        if tok.type != "EOF":
            self.pos += 1
        return tok

    def expect(self, type_):
        tok = self.peek()
        if tok.type != type_:
            raise ParseError(
                f"வரி {tok.line}: '{type_}' எதிர்பார்க்கப்பட்டது, ஆனால் '{tok.value}' கிடைத்தது "
                f"(expected {type_}, got {tok.type}:{tok.value!r})"
            )
        return self.advance()

    def skip_terminators(self):
        while self.at("NEWLINE", "SEMI"):
            self.advance()

    # ---- entry point ----
    def parse_program(self):
        stmts = []
        self.skip_terminators()
        while not self.at("EOF"):
            stmts.append(self.parse_statement())
            self.skip_terminators()
        return A.Program(stmts)

    def parse_block(self):
        self.expect("LBRACE")
        self.skip_terminators()
        stmts = []
        while not self.at("RBRACE", "EOF"):
            stmts.append(self.parse_statement())
            self.skip_terminators()
        self.expect("RBRACE")
        return stmts

    # ---- statements ----
    def parse_statement(self):
        tok = self.peek()
        if tok.type == "LET":
            return self.parse_let()
        if tok.type == "PRINT":
            return self.parse_print()
        if tok.type == "IF":
            return self.parse_if()
        if tok.type == "WHILE":
            return self.parse_while()
        if tok.type == "FOR":
            return self.parse_for()
        if tok.type == "FUNC":
            return self.parse_funcdef()
        if tok.type == "RETURN":
            line = self.advance().line
            if self.at("NEWLINE", "SEMI", "RBRACE", "EOF"):
                return A.ReturnStmt(None, line)
            return A.ReturnStmt(self.parse_expr(), line)
        if tok.type == "BREAK":
            line = self.advance().line
            return A.BreakStmt(line)
        if tok.type == "CONTINUE":
            line = self.advance().line
            return A.ContinueStmt(line)
        if tok.type == "IMPORT":
            return self.parse_import()
        # assignment or expression statement
        if tok.type == "IDENT":
            checkpoint = self.pos
            target = self.parse_postfix(self.parse_primary())
            if self.at("ASSIGN"):
                line = self.advance().line
                expr = self.parse_expr()
                return A.AssignStmt(target, expr, line)
            self.pos = checkpoint
        expr = self.parse_expr()
        return A.ExprStmt(expr, expr.line if hasattr(expr, "line") else tok.line)

    def parse_let(self):
        line = self.advance().line  # LET
        name = self.expect("IDENT").value
        self.expect("ASSIGN")
        expr = self.parse_expr()
        return A.LetStmt(name, expr, line)

    def parse_print(self):
        line = self.advance().line  # PRINT
        self.expect("LPAREN")
        args = []
        if not self.at("RPAREN"):
            args.append(self.parse_expr())
            while self.at("COMMA"):
                self.advance()
                args.append(self.parse_expr())
        self.expect("RPAREN")
        return A.PrintStmt(args, line)

    def parse_if(self):
        line = self.advance().line  # IF
        branches = []
        self.expect("LPAREN")
        cond = self.parse_expr()
        self.expect("RPAREN")
        body = self.parse_block()
        branches.append((cond, body))
        self.skip_terminators_lookahead()
        while self.at("ELIF"):
            self.advance()
            self.expect("LPAREN")
            c = self.parse_expr()
            self.expect("RPAREN")
            b = self.parse_block()
            branches.append((c, b))
            self.skip_terminators_lookahead()
        else_body = None
        if self.at("ELSE"):
            self.advance()
            else_body = self.parse_block()
        return A.IfStmt(branches, else_body, line)

    def skip_terminators_lookahead(self):
        # allow newlines between '}' and a following ELIF/ELSE
        save = self.pos
        while self.at("NEWLINE", "SEMI"):
            self.advance()
        if not self.at("ELIF", "ELSE"):
            self.pos = save

    def parse_while(self):
        line = self.advance().line
        self.expect("LPAREN")
        cond = self.parse_expr()
        self.expect("RPAREN")
        body = self.parse_block()
        return A.WhileStmt(cond, body, line)

    def parse_for(self):
        line = self.advance().line  # FOR
        name = self.expect("IDENT").value
        self.expect("IN")
        iterable = self.parse_expr()
        body = self.parse_block()
        return A.ForStmt(name, iterable, body, line)

    def parse_funcdef(self):
        line = self.advance().line  # FUNC
        name = self.expect("IDENT").value
        self.expect("LPAREN")
        params = []
        if not self.at("RPAREN"):
            params.append(self.expect("IDENT").value)
            while self.at("COMMA"):
                self.advance()
                params.append(self.expect("IDENT").value)
        self.expect("RPAREN")
        body = self.parse_block()
        return A.FuncDef(name, params, body, line)

    def parse_import(self):
        line = self.advance().line  # IMPORT
        mod_tok = self.expect("STRING")
        alias = None
        if self.at("AS"):
            self.advance()
            alias = self.expect("IDENT").value
        return A.ImportStmt(mod_tok.value, alias, line)

    # ---- expressions (precedence climbing) ----
    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.at("OR"):
            line = self.advance().line
            right = self.parse_and()
            left = A.BinOp("OR", left, right, line)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.at("AND"):
            line = self.advance().line
            right = self.parse_not()
            left = A.BinOp("AND", left, right, line)
        return left

    def parse_not(self):
        if self.at("NOT"):
            line = self.advance().line
            operand = self.parse_not()
            return A.UnaryOp("NOT", operand, line)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addsub()
        while self.at("EQ", "NEQ", "LT", "GT", "LE", "GE"):
            op = self.advance()
            right = self.parse_addsub()
            left = A.BinOp(op.type, left, right, op.line)
        return left

    def parse_addsub(self):
        left = self.parse_muldiv()
        while self.at("PLUS", "MINUS"):
            op = self.advance()
            right = self.parse_muldiv()
            left = A.BinOp(op.type, left, right, op.line)
        return left

    def parse_muldiv(self):
        left = self.parse_unary()
        while self.at("STAR", "SLASH", "PERCENT", "FLOORDIV"):
            op = self.advance()
            right = self.parse_unary()
            left = A.BinOp(op.type, left, right, op.line)
        return left

    def parse_unary(self):
        if self.at("MINUS", "PLUS"):
            op = self.advance()
            operand = self.parse_unary()
            return A.UnaryOp(op.type, operand, op.line)
        return self.parse_power()

    def parse_power(self):
        base = self.parse_postfix(self.parse_primary())
        if self.at("POW"):
            line = self.advance().line
            exponent = self.parse_unary()
            return A.BinOp("POW", base, exponent, line)
        return base

    def parse_postfix(self, node):
        while True:
            if self.at("LPAREN"):
                line = self.advance().line
                args = []
                if not self.at("RPAREN"):
                    args.append(self.parse_expr())
                    while self.at("COMMA"):
                        self.advance()
                        args.append(self.parse_expr())
                self.expect("RPAREN")
                node = A.Call(node, args, line)
            elif self.at("LBRACK"):
                line = self.advance().line
                idx = self.parse_expr()
                self.expect("RBRACK")
                node = A.Index(node, idx, line)
            elif self.at("DOT"):
                line = self.advance().line
                name = self.expect("IDENT").value
                node = A.Attr(node, name, line)
            else:
                break
        return node

    def parse_primary(self):
        tok = self.peek()
        if tok.type == "NUMBER":
            self.advance()
            return A.Number(tok.value)
        if tok.type == "STRING":
            self.advance()
            return A.String(tok.value)
        if tok.type == "TRUE":
            self.advance()
            return A.Bool(True)
        if tok.type == "FALSE":
            self.advance()
            return A.Bool(False)
        if tok.type == "NONE":
            self.advance()
            return A.NoneLit()
        if tok.type == "IDENT":
            self.advance()
            return A.Ident(tok.value, tok.line)
        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.expect("RPAREN")
            return expr
        if tok.type == "LBRACK":
            self.advance()
            items = []
            if not self.at("RBRACK"):
                items.append(self.parse_expr())
                while self.at("COMMA"):
                    self.advance()
                    items.append(self.parse_expr())
            self.expect("RBRACK")
            return A.ListLit(items)
        raise ParseError(f"வரி {tok.line}: எதிர்பாராத குறியீடு '{tok.value}' (unexpected token {tok.type})")


def parse(tokens):
    return Parser(tokens).parse_program()
