"""Proves the koans are honest: every blank fails, every solution passes,
the two directories mirror each other, and both match source/.

Run from the repo root with: pytest tests/
"""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import generate  # noqa: E402


def run_suite(directory: str, tmp_path: Path) -> dict[tuple[str, str], str]:
    """Run pytest on a directory in a subprocess and return {(file, koan): outcome}."""
    report = tmp_path / f"{directory}.xml"
    subprocess.run(
        [
            sys.executable, "-m", "pytest", directory,
            "--maxfail=0", "--tb=no", "-q", "-p", "no:cacheprovider",
            f"--junitxml={report}",
        ],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    outcomes = {}
    for case in ET.parse(report).getroot().iter("testcase"):
        key = (case.get("classname").split(".")[-1], case.get("name"))
        outcomes[key] = next((child.tag for child in case), "passed")
    return outcomes


@pytest.fixture(scope="session")
def koan_outcomes(tmp_path_factory):
    return run_suite("koans", tmp_path_factory.mktemp("koans"))


@pytest.fixture(scope="session")
def solution_outcomes(tmp_path_factory):
    return run_suite("solutions", tmp_path_factory.mktemp("solutions"))


def test_there_are_koans(koan_outcomes):
    assert len(koan_outcomes) > 150


def test_every_solution_passes(solution_outcomes):
    not_passing = {k: v for k, v in solution_outcomes.items() if v != "passed"}
    assert not_passing == {}


def test_every_unsolved_koan_fails_rather_than_errors_or_passes(koan_outcomes):
    wrong = {k: v for k, v in koan_outcomes.items() if v != "failure"}
    assert wrong == {}


def test_koans_and_solutions_mirror_each_other(koan_outcomes, solution_outcomes):
    assert set(koan_outcomes) == set(solution_outcomes)


def test_generated_files_match_source():
    stale = [
        path.relative_to(ROOT)
        for path, content in generate.generate(ROOT).items()
        if not path.exists() or path.read_text() != content
    ]
    assert stale == [], "run: python tools/generate.py"


def test_no_koan_compares_a_blank_with_not_equal():
    offenders = [
        f"{path.name}:{number}"
        for path in (ROOT / "source").glob("*_test.py")
        for number, line in enumerate(path.read_text().splitlines(), 1)
        if "_a(" in line and (" != " in line or " is not " in line)
    ]
    assert offenders == []


def test_every_block_is_closed():
    for path in (ROOT / "source").glob("*_test.py"):
        generate.render(path.read_text(), blank=True)


def test_every_file_with_a_block_has_an_implement_meditation():
    for path in (ROOT / "source").glob("*_test.py"):
        text = path.read_text()
        if generate.BLOCK_OPEN in text:
            assert "Implement " in text, path.name


def test_every_koan_has_a_meditation():
    missing = [
        f"{path.name}:{number}"
        for path in (ROOT / "source").glob("*_test.py")
        for number, (line, following) in enumerate(
            zip(path.read_text().splitlines(), path.read_text().splitlines()[1:]), 1
        )
        if line.startswith("def test_") and not following.strip().startswith('"""')
    ]
    assert missing == []
