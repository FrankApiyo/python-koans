"""Generate koans/ and solutions/ from source/.

In source/, a value answer is written as _a(value). A code answer is a run of
whole statements between a `# >>> answer` line and a `# <<<` line. This
script writes the same file to koans/ with each _a(value) replaced by __ and
each block replaced by a single __() line, and to solutions/ with the value
kept and the block's marker lines dropped. Run from the repo root:

    python tools/generate.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "_a("
BLOCK_OPEN = "# >>> answer"
BLOCK_CLOSE = "# <<<"


def _split_answers(text: str) -> list[tuple[str, str]]:
    """Return alternating (literal, answer) chunks. The last answer is ''."""
    chunks = []
    pos = 0
    while True:
        start = text.find(MARKER, pos)
        if start == -1:
            chunks.append((text[pos:], ""))
            return chunks
        end = _matching_paren(text, start + len(MARKER) - 1)
        chunks.append((text[pos:start], text[start + len(MARKER) : end]))
        pos = end + 1


def _matching_paren(text: str, open_index: int) -> int:
    depth = 0
    in_string = None
    i = open_index
    while i < len(text):
        ch = text[i]
        if in_string:
            if ch == "\\":
                i += 1
            elif text.startswith(in_string, i):
                i += len(in_string) - 1
                in_string = None
        elif ch == "#":
            i = text.index("\n", i)
        elif text.startswith(('"""', "'''"), i):
            in_string = text[i : i + 3]
            i += 2
        elif ch in "\"'":
            in_string = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"unbalanced _a( at offset {open_index}")


def _render_blocks(text: str, blank: bool) -> str:
    out = []
    inside = False
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        stripped = line.strip()
        if stripped == BLOCK_OPEN:
            if inside:
                raise ValueError(f"nested {BLOCK_OPEN} at line {number}")
            inside = True
            if blank:
                indent = line[: len(line) - len(line.lstrip())]
                out.append(f"{indent}__()\n")
        elif stripped == BLOCK_CLOSE:
            if not inside:
                raise ValueError(f"{BLOCK_CLOSE} without {BLOCK_OPEN} at line {number}")
            inside = False
        elif not (inside and blank):
            out.append(line)
    if inside:
        raise ValueError(f"{BLOCK_OPEN} never closed")
    return "".join(out)


def render(text: str, blank: bool) -> str:
    text = _render_blocks(text, blank)
    return "".join(
        literal + ("__" if blank and answer else answer)
        for literal, answer in _split_answers(text)
    )


def generate(root: Path = ROOT) -> dict[Path, str]:
    outputs = {}
    for src in sorted((root / "source").glob("*_test.py")):
        text = src.read_text()
        outputs[root / "koans" / src.name] = render(text, blank=True)
        outputs[root / "solutions" / src.name] = render(text, blank=False)
    return outputs


def main() -> None:
    for path, content in generate().items():
        path.parent.mkdir(exist_ok=True)
        path.write_text(content)
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
