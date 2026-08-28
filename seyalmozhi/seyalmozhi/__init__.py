"""செயல்மொழி (Seyal Mozhi) - a Tamil-keyword programming language."""
from .interpreter import Interpreter, SeyalRuntimeError
from .lexer import tokenize, LexError
from .parser import parse, ParseError

__version__ = "1.0.0"
__all__ = ["Interpreter", "SeyalRuntimeError", "tokenize", "LexError", "parse", "ParseError"]
