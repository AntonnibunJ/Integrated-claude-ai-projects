# செயல்மொழி (Seyal Mozhi) — a Tamil-keyword programming language

> "செயல்" (seyal) = action/doing, "மொழி" (mozhi) = language.
> A programming language whose keywords are Tamil words, built with a real
> lexer → parser → tree-walking interpreter, designed to be simpler to read
> than Python, with the ability to call directly into Python (and, through
> Python, virtually any C-backed library) for integration.

## Honest scope note

This is a genuine, working interpreted language (not a keyword find-and-replace
over Python). It is **not** a from-scratch machine-code compiler that
outperforms C — that is a multi-year systems-engineering project (this is
essentially what projects like LLVM exist to do). What's delivered here:

- A real lexer, parser, and evaluator, written from scratch.
- Syntax deliberately simpler than Python's (explicit `{ }` blocks instead of
  significant whitespace, fewer special cases).
- Direct interoperability with Python via `இறக்குமதி` (import), so you can
  call `math`, `random`, `json`, or literally any installed Python package
  — this is the "integrate with other languages" bridge.
- A full automated test suite (`tests/`).
- A browser-based IDE (black & white theme) that runs a JavaScript port of
  the same language live, no install needed.

Performance is that of a tree-walking interpreter (similar ballpark to
CPython for equivalent code) — fast enough for scripts, teaching, automation,
and glue code. It is not competing with compiled C on raw number-crunching.

## Why Tamil keywords, and why these particular words

The keywords are drawn from plain, commonly-used modern Tamil (the kind
you'd see in a newspaper), not obscure classical vocabulary, so anyone
literate in Tamil today can read code aloud and understand it immediately —
e.g. `செயல்` (function/action) and `திருப்பு` (return/turn back) are words
in everyday use. Classical Tamil literature (e.g. the Thirukkural's use of
"செயல்" to mean "action/deed") inspired a couple of the word choices for
their precision, but every keyword was then checked against contemporary
usage so the language stays approachable rather than archaic.

---

## 1. Installation & running a program

```bash
python3 -m seyalmozhi.cli your_program.sm
```

Or from Python code:

```python
from seyalmozhi import Interpreter
Interpreter().run(open("your_program.sm", encoding="utf-8").read())
```

File extension convention: `.sm`

---

## 2. Syntax at a glance

| Concept              | Seyal Mozhi keyword | Meaning (literal)      | Example |
|----------------------|----------------------|-------------------------|---------|
| declare variable     | `வை`                 | "put/place"             | `வை x = 5` |
| print                | `அச்சிடு`            | "print"                 | `அச்சிடு("வணக்கம்")` |
| if                   | `என்றால்`            | "if"                    | `என்றால் (x > 0) { ... }` |
| else if              | `இல்லைஎன்றால்`       | "else if"               | `இல்லைஎன்றால் (x == 0) { ... }` |
| else                 | `இல்லை`              | "no/otherwise"          | `இல்லை { ... }` |
| while loop           | `வரைக்கும்`          | "until"                 | `வரைக்கும் (x < 10) { ... }` |
| for-each loop        | `ஒவ்வொன்றாக ... இல்` | "each one ... in"       | `ஒவ்வொன்றாக n இல் பட்டியல் { ... }` |
| function definition  | `செயல்`              | "action"                | `செயல் கூட்டு(a, b) { ... }` |
| return               | `திருப்பு`           | "turn back / return"    | `திருப்பு x + 1` |
| break                | `நிறுத்து`           | "stop"                  | `நிறுத்து` |
| continue             | `தொடர்`              | "continue"              | `தொடர்` |
| true / false         | `உண்மை` / `பொய்`     | "truth" / "lie"         | `வை ok = உண்மை` |
| none / null          | `வெறுமை`             | "emptiness"             | `வை x = வெறுமை` |
| and / or / not       | `மற்றும்` / `அல்லது` / `அல்ல` | | `a மற்றும் b` |
| import               | `இறக்குமதி`          | "import"                | `இறக்குமதி "math" ஆக கணிதம்` |
| comment              | `#`                  |                          | `# இது ஒரு குறிப்பு` |

Blocks use `{ }` (like C/JavaScript) rather than significant indentation —
this removes the single most common source of beginner errors in
whitespace-sensitive languages. Statements end at a newline (no semicolons
needed, though `;` is accepted).

---

## 3. Language rules, in detail

### 3.1 Variables
```
வை பெயர் = "தமிழ்"      # declare
பெயர் = "மொழி"           # reassign (no வை needed again)
```
Variables are dynamically typed, same as Python — a name can hold a number,
string, boolean, list, function, or imported module.

### 3.2 Data types
- Numbers: `5`, `3.14` (int and float, same semantics as Python)
- Strings: `"..."` or `'...'`, with `\n`, `\t`, `\\`, `\"`, `\'` escapes
- Booleans: `உண்மை` (true), `பொய்` (false)
- None: `வெறுமை`
- Lists: `[1, 2, 3]`, indexed with `எண்கள்[0]`

### 3.3 Operators
Arithmetic: `+  -  *  /  //  %  **`
Comparison: `==  !=  <  >  <=  >=`
Logical: `மற்றும்` (and), `அல்லது` (or), `அல்ல` (not)

### 3.4 Conditionals
```
என்றால் (x > 90) {
    அச்சிடு("A")
} இல்லைஎன்றால் (x > 75) {
    அச்சிடு("B")
} இல்லை {
    அச்சிடு("C")
}
```

### 3.5 Loops
```
வரைக்கும் (i < 5) {          # while
    அச்சிடு(i)
    i = i + 1
}

ஒவ்வொன்றாக n இல் வரம்பு(5) {  # for n in range(5)
    அச்சிடு(n)
}
```
`நிறுத்து` exits the nearest loop; `தொடர்` skips to the next iteration.

### 3.6 Functions
```
செயல் பிப(n) {
    என்றால் (n <= 1) { திருப்பு n }
    திருப்பு பிப(n - 1) + பிப(n - 2)
}
அச்சிடு(பிப(10))     # 55
```
Functions are first-class values (can be passed around, returned, and form
closures over enclosing variables), and support recursion.

### 3.7 Lists & built-in functions
```
வை a = [3, 1, 2]
சேர்(a, 9)              # append -> [3, 1, 2, 9]
அச்சிடு(நீளம்(a))       # length -> 4
அச்சிடு(வரிசைப்படுத்து(a))  # sort -> [1, 2, 3, 9]
```

Built-ins provided: `நீளம்` (len), `வரம்பு` (range), `எண்ணாக்கு` (int),
`தசமமாக்கு` (float), `சரமாக்கு` (str), `உள்ளீடு` (input), `சேர்` (append),
`நீக்கு` (remove/pop), `வரிசைப்படுத்து` (sort), `அதிகபட்சம்` (max),
`குறைந்தபட்சம்` (min), `முழுமையாக` (abs), `வகை` (type).

### 3.8 Integrating with other languages (Python interop)
```
இறக்குமதி "math" ஆக கணிதம்
அச்சிடு(கணிதம்.sqrt(81))     # 9.0
அச்சிடு(கணிதம்.pi)
```
`இறக்குமதி "<module>" ஆக <பெயர்>` imports any installed Python module and
binds it under a Tamil alias. Since virtually every ecosystem (C, Rust,
Java, etc.) has Python bindings, this is the practical bridge for using
other languages' libraries from Seyal Mozhi.

### 3.9 Comments
```
# இது ஒரு வரி குறிப்பு (a single-line comment)
```

---

## 4. Error messages

Errors are reported bilingually with a line number, e.g.:

```
பிழை (error): வரி 3: 'எண்' எனும் பெயர் அறியப்படவில்லை (undefined name)
```

## 5. Testing

```bash
python3 -m pytest tests/ -v        # if pytest is installed
python3 tests/run_tests.py         # zero-dependency fallback runner
```
22 tests cover the lexer, parser, control flow, functions/closures/recursion,
lists, error handling, and Python interop.

## 6. The IDE

`ide.html` is a self-contained, black-and-white themed code editor that runs
a JavaScript port of this same language directly in your browser — open it
in any browser, no installation needed. It includes example programs,
line-numbered editing, and a run/output console.

## 7. Project layout

```
seyalmozhi/
  seyalmozhi/
    lexer.py         # source text -> tokens
    parser.py         # tokens -> AST
    ast_nodes.py       # AST node definitions
    interpreter.py     # AST -> execution, built-ins, Python interop
    cli.py              # command-line runner
  examples/            # sample .sm programs
  tests/               # automated test suite
  ide.html             # browser IDE (black & white theme)
  README.md
```
