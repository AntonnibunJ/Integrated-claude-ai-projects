"""
Lexer for செயல்மொழி (Seyal Mozhi) - a Tamil-keyword programming language.
Turns raw source text into a flat list of Token objects.
"""

import re

KEYWORDS = {
    "வை": "LET",            # declare a variable      -> "வை x = 5"
    "மாறி": "LET",           # alt word for declare (variable)
    "அச்சிடு": "PRINT",       # print
    "என்றால்": "IF",          # if
    "இல்லைஎன்றால்": "ELIF",   # else if
    "இல்லை": "ELSE",          # else
    "வரைக்கும்": "WHILE",     # while ("until")
    "ஒவ்வொன்றாக": "FOR",      # for (each)
    "இல்": "IN",              # in
    "செயல்": "FUNC",          # function/action definition
    "திருப்பு": "RETURN",     # return
    "நிறுத்து": "BREAK",      # break
    "தொடர்": "CONTINUE",      # continue
    "உண்மை": "TRUE",          # true
    "பொய்": "FALSE",          # false
    "வெறுமை": "NONE",         # none / null (emptiness)
    "மற்றும்": "AND",         # and
    "அல்லது": "OR",           # or
    "அல்ல": "NOT",            # not
    "இறக்குமதி": "IMPORT",    # import (bring in another module/language)
    "ஆக": "AS",               # as (used in import ... ஆக alias)
}

TOKEN_SPEC = [
    ("SKIP",      r"[ \t]+"),
    ("COMMENT",   r"#[^\n]*"),
    ("NEWLINE",   r"\n"),
    ("NUMBER",    r"\d+\.\d+|\d+"),
    ("STRING",    r'"([^"\\]|\\.)*"' + r"|'([^'\\]|\\.)*'"),
    ("POW",       r"\*\*"),
    ("FLOORDIV",  r"//"),
    ("EQ",        r"=="),
    ("NEQ",       r"!="),
    ("LE",        r"<="),
    ("GE",        r">="),
    ("ASSIGN",    r"="),
    ("LT",        r"<"),
    ("GT",        r">"),
    ("PLUS",      r"\+"),
    ("MINUS",     r"-"),
    ("STAR",      r"\*"),
    ("SLASH",     r"/"),
    ("PERCENT",   r"%"),
    ("LPAREN",    r"\("),
    ("RPAREN",    r"\)"),
    ("LBRACE",    r"\{"),
    ("RBRACE",    r"\}"),
    ("LBRACK",    r"\["),
    ("RBRACK",    r"\]"),
    ("COMMA",     r","),
    ("COLON",     r":"),
    ("DOT",       r"\."),
    ("SEMI",      r";"),
    # An identifier: Tamil letters/vowel-signs, ASCII letters, digits, underscore.
    # Tamil Unicode block: U+0B80-U+0BFF
    ("IDENT",     r"[A-Za-z_\u0B80-\u0BFF][A-Za-z0-9_\u0B80-\u0BFF]*"),
]

MASTER_RE = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))


class Token:
    __slots__ = ("type", "value", "line")

    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


class LexError(Exception):
    pass


_ESCAPES = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    '"': '"',
    "'": "'",
    "\\": "\\",
}


def _unescape(raw: str) -> str:
    """Handle a small, explicit set of backslash escapes without touching
    non-ASCII characters (Tamil text must pass through untouched)."""
    out = []
    i = 0
    n = len(raw)
    while i < n:
        ch = raw[i]
        if ch == "\\" and i + 1 < n and raw[i + 1] in _ESCAPES:
            out.append(_ESCAPES[raw[i + 1]])
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def tokenize(source: str):
    tokens = []
    line = 1
    pos = 0
    length = len(source)
    while pos < length:
        m = MASTER_RE.match(source, pos)
        if not m:
            bad = source[pos]
            raise LexError(f"வரி {line}: புரியாத எழுத்து '{bad}' (unexpected character)")
        kind = m.lastgroup
        text = m.group()
        pos = m.end()
        if kind == "NEWLINE":
            tokens.append(Token("NEWLINE", "\n", line))
            line += 1
            continue
        if kind in ("SKIP", "COMMENT"):
            continue
        if kind == "IDENT":
            if text in KEYWORDS:
                tokens.append(Token(KEYWORDS[text], text, line))
            else:
                tokens.append(Token("IDENT", text, line))
        elif kind == "STRING":
            raw = text[1:-1]
            raw = _unescape(raw)
            tokens.append(Token("STRING", raw, line))
        elif kind == "NUMBER":
            if "." in text:
                tokens.append(Token("NUMBER", float(text), line))
            else:
                tokens.append(Token("NUMBER", int(text), line))
        else:
            tokens.append(Token(kind, text, line))
    tokens.append(Token("EOF", None, line))
    return tokens
