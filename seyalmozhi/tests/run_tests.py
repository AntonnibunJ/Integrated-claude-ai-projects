"""
Fallback test runner for environments without pytest installed.
Usage: python3 tests/run_tests.py
(If pytest IS installed, prefer: python3 -m pytest tests/ -v)
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(__file__))


class FakeRaises:
    """Minimal stand-in for pytest.raises(...) used as a context manager."""
    def __init__(self, exc_type):
        self.exc_type = exc_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"Expected {self.exc_type.__name__} but nothing was raised")
        if not issubclass(exc_type, self.exc_type):
            return False
        return True  # suppress the expected exception


class FakePytest:
    @staticmethod
    def raises(exc_type):
        return FakeRaises(exc_type)

    @staticmethod
    def main(args):
        return 0


sys.modules["pytest"] = FakePytest()  # let test_seyalmozhi.py's `import pytest` work

import test_seyalmozhi as t  # noqa: E402


def main():
    tests = [name for name in dir(t) if name.startswith("test_")]
    passed, failed = 0, 0
    for name in tests:
        fn = getattr(t, name)
        try:
            fn()
            print(f"பாஸ் (PASS): {name}")
            passed += 1
        except Exception:
            print(f"தோல்வி (FAIL): {name}")
            traceback.print_exc()
            failed += 1
    total = passed + failed
    print(f"\n{passed}/{total} தேர்வுகள் வெற்றி (tests passed)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
