"""
Testing environment for செயல்மொழி (Seyal Mozhi).
Run with:  python3 -m pytest tests/ -v
"""
import io
import contextlib
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from seyalmozhi.interpreter import Interpreter, SeyalRuntimeError
from seyalmozhi.lexer import tokenize, LexError
from seyalmozhi.parser import parse, ParseError


def run(source):
    """Run source, return captured stdout as a string."""
    interp = Interpreter()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        interp.run(source)
    return buf.getvalue()


# ---------------- Lexer ----------------

def test_lexer_keywords():
    toks = tokenize("வை x = 5")
    types = [t.type for t in toks]
    assert types == ["LET", "IDENT", "ASSIGN", "NUMBER", "EOF"]


def test_lexer_numbers_and_strings():
    toks = tokenize('3.14 "வணக்கம்"')
    assert toks[0].type == "NUMBER" and toks[0].value == 3.14
    assert toks[1].type == "STRING" and toks[1].value == "வணக்கம்"


def test_lexer_rejects_bad_char():
    import pytest
    with pytest.raises(LexError):
        tokenize("வை x = 5 @")


# ---------------- Parser ----------------

def test_parse_simple_program():
    tree = parse(tokenize('அச்சிடு("வணக்கம்")'))
    assert len(tree.statements) == 1


def test_parse_error_on_bad_syntax():
    import pytest
    with pytest.raises(ParseError):
        parse(tokenize("என்றால் (x > 1"))  # missing RPAREN / block


# ---------------- Interpreter: basics ----------------

def test_print_and_variables():
    out = run('வை பெயர் = "தமிழ்"\nஅச்சிடு("வணக்கம்", பெயர்)')
    assert out.strip() == "வணக்கம் தமிழ்"


def test_arithmetic():
    out = run("அச்சிடு(2 + 3 * 4)")
    assert out.strip() == "14"


def test_string_concat():
    out = run('அச்சிடு("a" + "b")')
    assert out.strip() == "ab"


def test_boolean_and_none_printing():
    out = run("அச்சிடு(உண்மை, பொய், வெறுமை)")
    assert out.strip() == "உண்மை பொய் வெறுமை"


def test_reassignment():
    out = run("வை x = 1\nx = x + 1\nx = x + 1\nஅச்சிடு(x)")
    assert out.strip() == "3"


# ---------------- Control flow ----------------

def test_if_else():
    src = """
    வை x = 10
    என்றால் (x > 5) {
        அச்சிடு("பெரியது")
    } இல்லை {
        அச்சிடு("சிறியது")
    }
    """
    assert run(src).strip() == "பெரியது"


def test_elif_chain():
    src = """
    செயல் தரம்(மதிப்பெண்) {
        என்றால் (மதிப்பெண் >= 90) {
            திருப்பு "A"
        } இல்லைஎன்றால் (மதிப்பெண் >= 75) {
            திருப்பு "B"
        } இல்லை {
            திருப்பு "C"
        }
    }
    அச்சிடு(தரம்(95))
    அச்சிடு(தரம்(80))
    அச்சிடு(தரம்(40))
    """
    assert run(src).splitlines() == ["A", "B", "C"]


def test_while_loop_and_break():
    src = """
    வை i = 0
    வரைக்கும் (உண்மை) {
        என்றால் (i == 3) {
            நிறுத்து
        }
        அச்சிடு(i)
        i = i + 1
    }
    """
    assert run(src).splitlines() == ["0", "1", "2"]


def test_for_loop_continue():
    src = """
    ஒவ்வொன்றாக i இல் வரம்பு(5) {
        என்றால் (i % 2 == 0) {
            தொடர்
        }
        அச்சிடு(i)
    }
    """
    assert run(src).splitlines() == ["1", "3"]


# ---------------- Functions / recursion ----------------

def test_function_and_recursion():
    src = """
    செயல் பிப(n) {
        என்றால் (n <= 1) {
            திருப்பு n
        }
        திருப்பு பிப(n - 1) + பிப(n - 2)
    }
    அச்சிடு(பிப(10))
    """
    assert run(src).strip() == "55"


def test_closures():
    src = """
    செயல் எண்ணி() {
        வை count = 0
        செயல் அதிகரி() {
            count = count + 1
            திருப்பு count
        }
        திருப்பு அதிகரி
    }
    """
    interp = Interpreter()
    interp.run(src)
    make_counter = interp.globals.get("எண்ணி")
    counter = make_counter()
    assert counter() == 1
    assert counter() == 2
    assert counter() == 3


# ---------------- Data structures ----------------

def test_lists_and_builtins():
    src = """
    வை நிலை = [3, 1, 2]
    சேர்(நிலை, 9)
    அச்சிடு(நீளம்(நிலை))
    அச்சிடு(வரிசைப்படுத்து(நிலை))
    """
    lines = run(src).splitlines()
    assert lines[0] == "4"
    assert lines[1] == "[1, 2, 3, 9]"


def test_list_indexing():
    out = run("வை a = [10, 20, 30]\nஅச்சிடு(a[1])")
    assert out.strip() == "20"


# ---------------- Errors ----------------

def test_undefined_variable_raises():
    import pytest
    with pytest.raises(SeyalRuntimeError):
        run("அச்சிடு(இல்லாதது)")


def test_division_by_zero_raises():
    import pytest
    with pytest.raises(SeyalRuntimeError):
        run("அச்சிடு(1 / 0)")


def test_wrong_arg_count_raises():
    import pytest
    with pytest.raises(SeyalRuntimeError):
        run("செயல் கூட்டு(a, b) { திருப்பு a + b }\nஅச்சிடு(கூட்டு(1))")


# ---------------- Python interop ----------------

def test_python_module_import():
    src = """
    இறக்குமதி "math" ஆக கணிதம்
    அச்சிடு(கணிதம்.sqrt(16))
    """
    assert run(src).strip() == "4.0"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
