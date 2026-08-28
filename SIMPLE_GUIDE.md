# செயல்மொழி (Seyal Mozhi) — Simple Guide (for absolute beginners)

This page explains the project in the simplest possible words.
No coding background needed to read this.

---

## 1. What even is this?

**செயல்மொழி (say it: "say-yal mo-zhi")** is a new computer programming
language — like Python or C — but its commands are Tamil words instead of
English words.

Example: instead of typing `print("Hello")` like in Python, you type:
```
அச்சிடு("வணக்கம்")
```
Same idea, Tamil words.

---

## 2. What's inside the folder (map of the project)

When you unzip `seyalmozhi.zip`, you'll see this:

```
seyalmozhi/
├── README.md              👉 THE RULEBOOK — all the syntax & grammar rules live here
├── ide.html                👉 THE APP — open this to write & run code, no install needed
├── examples/                a few ready-made sample programs to try
├── tests/                    automated checks proving the language works correctly
└── seyalmozhi/               the actual "engine" code that runs the language (Python files)
```

**📖 Where are the syntax rules?**
Open **`README.md`**. That is the rulebook — it lists every keyword (like
`வை`, `அச்சிடு`, `என்றால்`), what it means, and how to write `if`
statements, loops, functions, lists, etc. Anyone can open this file in any
web browser or text editor and read it like a manual.

---

## 3. Which "environment" do you need to run it?

There are **two ways** to run this. Pick whichever is easier for you.

### 🟢 Option A — Easiest, zero install (recommended for most people)
Just double-click **`ide.html`**. It opens in your normal web browser
(Chrome, Edge, Firefox, Safari — anything). That's it. You type code on
the left, press the **"▶ ஓடு (Run)"** button, and see the output on the
right — just like Python's IDLE or old Turbo C, but in your browser.

**What your computer needs for Option A:**
- A web browser. That's the ONLY requirement.
- No installation, no internet connection needed after you have the file,
  no extra software.
- Works on Windows, Mac, Linux, even a tablet.

### 🟡 Option B — Run it from the command line (for people comfortable with code)
This uses the actual Python engine files.

**What your computer needs for Option B:**
- **Python 3** installed on the computer (version 3.8 or newer).
  - Check by opening a terminal/command prompt and typing: `python3 --version`
  - If it's not installed, download it free from python.org
- Nothing else — no extra libraries or packages need to be installed.
  (It only uses Python's built-in tools.)

**How to run it (Option B), step by step:**
1. Unzip the `seyalmozhi.zip` folder anywhere on your computer.
2. Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux).
3. Go into the folder:
   ```
   cd seyalmozhi
   ```
4. Run any sample program with this command:
   ```
   python3 -m seyalmozhi.cli examples/vanakkam.sm
   ```
5. You should see Tamil text printed out. That means it worked!

To run your OWN program: write your code in a new text file, save it with
a `.sm` ending (for example `என்_நிரல்.sm`), then run:
```
python3 -m seyalmozhi.cli என்_நிரல்.sm
```

---

## 4. Quick example to try right now

Paste this into `ide.html` (or a `.sm` file):
```
அச்சிடு("வணக்கம் உலகம்!")

வை பெயர் = "தமிழ்"
அச்சிடு("என் மொழியின் பெயர்:", பெயர்)
```
Expected output:
```
வணக்கம் உலகம்!
என் மொழியின் பெயர்: தமிழ்
```

---

## 5. Summary table (for the impatient)

| Question | Answer |
|---|---|
| Where are the rules/syntax? | `README.md` |
| Easiest way to try it? | Open `ide.html` in any browser |
| Anything to install for that? | Nothing. Just a browser. |
| Command-line way? | `python3 -m seyalmozhi.cli file.sm` |
| Needs Python? | Yes, Python 3.8+, no extra packages |
| Works on Windows/Mac/Linux? | Yes, all of them |
| Where are sample programs? | `examples/` folder |
| How do I know it actually works? | Run `python3 tests/run_tests.py` — it checks everything automatically |

---

*செயல்மொழி is a hobby/learning project: a real working interpreted
language, built to be simpler to read than Python, using Tamil keywords.
It is not a compiled, machine-code-level language like C — see the main
README for the full technical explanation of how it works under the hood.*
