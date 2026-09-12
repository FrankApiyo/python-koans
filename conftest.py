import re
from pathlib import Path

import pytest


class _Blank(str):
    """The blank you fill in. Compares equal to nothing, so a koan cannot pass
    until you replace it. Calling it raises, so a blanked method body fails
    on its own line."""

    def __new__(cls):
        return str.__new__(cls, "__")

    def __repr__(self):
        return "__"

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    def __hash__(self):
        return id(self)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Replace __() with the code the meditation describes")


__ = _Blank()

_first_failure = {}
_collected = {"total": 0, "in_suite": 0}


KOAN_DIRS = ("koans/", "solutions/")
ROOT = Path(__file__).resolve().parent


def _is_koan(item):
    return item.location[0].startswith(KOAN_DIRS)


def _koans_in(directory):
    """How many koans the whole directory holds, whether or not they were collected."""
    return sum(
        len(re.findall(r"^def test_", path.read_text(), re.MULTILINE))
        for path in (ROOT / directory).glob("*_test.py")
    )


def pytest_collection_finish(session):
    koans = [item for item in session.items if _is_koan(item)]
    _collected["total"] = len(koans)
    if koans:
        _collected["in_suite"] = _koans_in(koans[0].location[0].split("/")[0])


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    yield
    if call.excinfo is None or _first_failure or call.when != "call" or not _is_koan(item):
        return
    in_koan = [entry for entry in call.excinfo.traceback if entry.path == item.path]
    line = (in_koan[-1].lineno if in_koan else item.location[1]) + 1
    _first_failure.update(
        path=item.location[0],
        line=line,
        doc=(item.function.__doc__ or "").strip(),
    )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    tr = terminalreporter
    total = _collected["total"]
    if not total:
        return
    passed = sum(1 for r in tr.stats.get("passed", []) if r.location[0].startswith(KOAN_DIRS))
    in_suite = _collected["in_suite"]
    if _first_failure:
        f = _first_failure
        tr.write_sep("-", "The master says")
        tr.write_line(f"Meditate on {f['path']}:{f['line']}")
        if f["doc"]:
            tr.write_line(f"    {f['doc']}")
        tr.write_line(f"{passed} of {in_suite} koans answered.")
    elif exitstatus == 0 and passed == in_suite:
        tr.write_sep("-", "Enlightenment")
        tr.write_line(f"All {in_suite} koans pass. Start again with: git checkout -- koans/")
    elif exitstatus == 0:
        tr.write_line(f"{passed} of {in_suite} koans answered. Run the whole suite for the rest.")
