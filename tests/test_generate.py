import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import generate  # noqa: E402

SOURCE = '''def test_x():
    assert 1 == _a(1)


class Stack:
    def push(self, item):
        self._items.append(item)

    def pop(self):
        # >>> answer
        if not self._items:
            raise IndexError
        return self._items.pop()
        # <<<
'''


def test_value_blank_becomes_dunder_in_koan():
    assert "assert 1 == __\n" in generate.render(SOURCE, blank=True)


def test_value_blank_becomes_answer_in_solution():
    assert "assert 1 == 1\n" in generate.render(SOURCE, blank=False)


def test_block_becomes_one_called_blank_in_koan():
    out = generate.render(SOURCE, blank=True)
    assert "    def pop(self):\n        __()\n" in out
    assert ">>>" not in out and "<<<" not in out


def test_block_body_kept_and_markers_dropped_in_solution():
    out = generate.render(SOURCE, blank=False)
    assert "        return self._items.pop()\n" in out
    assert ">>>" not in out and "<<<" not in out


def test_unmatched_marker_raises():
    with pytest.raises(ValueError):
        generate.render("    # >>> answer\n    x = 1\n", blank=True)
    with pytest.raises(ValueError):
        generate.render("    x = 1\n    # <<<\n", blank=True)
