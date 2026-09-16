"""How a koan works.

Every file in koans/ is a list of tiny tests. Each has a blank, written __.
Replace the blank with whatever makes the assertion true, save, run again.
The runner stops at the first failure and prints the file and line to look
at, plus the koan's docstring, which we call the meditation.

There are two kinds of blank. A plain __ stands for a value: a number, a
string, a list. A __() on a line of its own stands for code you write. It
sits where a method body should be, and the meditation tells you what the
method must do, step by step. Until you replace it, calling that method
raises NotImplementedError and the footer points straight at it.

Each file starts with a lesson like this one. Read it once before the koans.
Between the lesson, the earlier chapters, and each meditation, you have
everything a koan needs. Nothing here requires looking anything up.

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

from conftest import __


def test_a_koan_has_a_blank():
    """Replace __ with whatever makes the assertion true, save, run again."""
    assert 1 + 1 == 2


def test_the_footer_tells_you_where_to_look():
    """The runner stops at the first failure and prints the file and line. Go there."""
    assert "koan".upper() == "KOAN"


class Greeter:
    def greet(self, name):
        return f"hello {name}"


def test_a_called_blank_is_code_you_write():
    """Implement Greeter.greet above. 1. Replace the whole __() line with a return of the string "hello " followed by name."""
    assert Greeter().greet("koan") == "hello koan"


def test_you_can_always_start_over():
    """git checkout -- koans/ restores every blank. Repetition is the point."""
    assert len("__") == 2
