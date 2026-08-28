"""Command-line runner: python -m seyalmozhi.cli program.sm"""
import sys
from .interpreter import Interpreter, SeyalRuntimeError
from .lexer import LexError
from .parser import ParseError


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print("பயன்பாடு (usage): python -m seyalmozhi.cli <file.sm>")
        return 1
    path = argv[0]
    with open(path, encoding="utf-8") as f:
        source = f.read()
    interp = Interpreter()
    try:
        interp.run(source, filename=path)
    except (LexError, ParseError, SeyalRuntimeError) as e:
        print(f"பிழை (error): {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
