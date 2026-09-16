"""Write the lesson diagrams to lessons/svg/ as standalone coloured SVG files.

Run from the repo root:

    python tools/diagrams.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "lessons" / "svg"

BG = "#fafaf9"
INK = "#1f2937"
MUTED = "#6b7280"
BLUE = "#2563eb"
ORANGE = "#ea580c"
GREEN = "#16a34a"
RED = "#dc2626"
PURPLE = "#7c3aed"
FILL_BLUE = "#dbeafe"
FILL_ORANGE = "#ffedd5"
FILL_GREEN = "#dcfce7"
FILL_YELLOW = "#fef3c7"
FILL_GREY = "#e5e7eb"
FILL_PURPLE = "#ede9fe"
FILL_RED = "#fee2e2"

SANS = "ui-sans-serif, system-ui, sans-serif"
MONO = "ui-monospace, Menlo, Consolas, monospace"

COLORS = {"ink": INK, "muted": MUTED, "blue": BLUE, "orange": ORANGE, "green": GREEN, "red": RED, "purple": PURPLE}


class Svg:
    def __init__(self, width, height, label):
        self.w = width
        self.h = height
        self.label = label
        self.parts = []

    def rect(self, x, y, w, h, fill="none", stroke=INK, rx=4, width=1.5, dashed=False):
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{dash}/>'
        )

    def circle(self, cx, cy, r, fill="none", stroke=INK, width=1.5):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def text(self, x, y, s, size=13, anchor="middle", fill=INK, weight="normal", mono=False, italic=False):
        family = MONO if mono else SANS
        style = ' font-style="italic"' if italic else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{style}>{s}</text>'
        )

    def line(self, x1, y1, x2, y2, stroke=INK, arrow=True, dashed=False, width=1.5):
        name = next(k for k, v in COLORS.items() if v == stroke)
        marker = f' marker-end="url(#arrow-{name})"' if arrow else ""
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}"{dash}{marker}/>'
        )

    def path(self, d, stroke=INK, arrow=True, dashed=False, width=1.5, fill="none"):
        name = next(k for k, v in COLORS.items() if v == stroke)
        marker = f' marker-end="url(#arrow-{name})"' if arrow else ""
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{dash}{marker}/>')

    def box(self, x, y, w, h, label, fill="none", stroke=INK, mono=True, size=13, sub=None):
        self.rect(x, y, w, h, fill=fill, stroke=stroke)
        dy = -4 if sub else 5
        self.text(x + w / 2, y + h / 2 + dy, label, size=size, mono=mono)
        if sub:
            self.text(x + w / 2, y + h / 2 + 12, sub, size=10, fill=MUTED)

    def save(self, name):
        defs = "".join(
            f'<marker id="arrow-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{v}"/></marker>'
            for k, v in COLORS.items()
        )
        body = "\n".join(self.parts)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img" aria-label="{self.label}">\n'
            f"<defs>{defs}</defs>\n"
            f'<rect width="{self.w}" height="{self.h}" fill="{BG}"/>\n'
            f"{body}\n</svg>\n"
        )
        (OUT / name).write_text(svg)
        print(f"lessons/svg/{name}")


def attribute_lookup():
    s = Svg(720, 300, "Attribute lookup checks the instance dict, then the class dict")
    for row, (y, title, inst, hit_inst) in enumerate([
        (30, 'rex.species  before any assignment', 'name: "Rex"', False),
        (170, 'rex.species  after  rex.species = "wolf"', 'name: "Rex"  species: "wolf"', True),
    ]):
        s.text(20, y, title, size=13, anchor="start", mono=True, weight="bold")
        s.rect(20, y + 20, 250, 70, fill=FILL_BLUE if hit_inst else "none")
        s.text(145, y + 40, "vars(rex)", size=12, fill=MUTED)
        s.text(145, y + 65, inst, size=12, mono=True)
        s.rect(420, y + 20, 280, 70, fill="none" if hit_inst else FILL_BLUE)
        s.text(560, y + 40, "vars(Dog)", size=12, fill=MUTED)
        s.text(560, y + 65, 'species: "Canis familiaris"  speak', size=11, mono=True)
        s.line(270, y + 55, 415, y + 55, stroke=MUTED if hit_inst else BLUE, dashed=hit_inst)
        if hit_inst:
            s.text(342, y + 48, "never asked", size=11, fill=MUTED)
            s.text(145, y + 105, "1  hit, stop here", size=12, fill=BLUE, weight="bold")
        else:
            s.text(145, y + 105, "1  miss", size=12, fill=MUTED)
            s.text(342, y + 48, "2  look in the class", size=11, fill=BLUE)
            s.text(560, y + 105, "hit: \"Canis familiaris\"", size=12, fill=BLUE, weight="bold")
    s.text(360, 290, "Assigning through an instance writes its own dict. The class dict is never changed.", size=12, fill=MUTED)
    s.save("01_attribute_lookup.svg")


def mro_diamond():
    s = Svg(720, 300, "The diamond D(B, C) and the linear MRO Python derives from it")
    nodes = {"A": (150, 50), "B": (70, 140), "C": (230, 140), "D": (150, 230)}
    for name, (x, y) in nodes.items():
        s.circle(x, y, 22, fill=FILL_BLUE if name == "D" else "none")
        s.text(x, y + 5, name, size=15, weight="bold")
    for child, parent in [("B", "A"), ("C", "A"), ("D", "B"), ("D", "C")]:
        (x1, y1), (x2, y2) = nodes[child], nodes[parent]
        dx, dy = x2 - x1, y2 - y1
        n = (dx * dx + dy * dy) ** 0.5
        s.line(x1 + dx / n * 24, y1 + dy / n * 24, x2 - dx / n * 26, y2 - dy / n * 26, stroke=MUTED)
    s.text(150, 275, "arrows mean \"inherits from\"", size=11, fill=MUTED)
    s.text(420, 45, "D.__mro__", size=13, mono=True, weight="bold", anchor="start")
    order = ["D", "B", "C", "A", "object"]
    x = 420
    for i, name in enumerate(order):
        w = 64 if name == "object" else 40
        s.rect(x, 60, w, 30, fill=FILL_ORANGE if name in ("B", "C") else "none")
        s.text(x + w / 2, 80, name, size=12, mono=True)
        if i < len(order) - 1:
            s.line(x + w, 75, x + w + 6, 75, stroke=MUTED, arrow=False)
        x += w + 6
    s.text(420, 120, "left to right, each class once,", size=12, anchor="start", fill=MUTED)
    s.text(420, 138, "a class always before its parents", size=12, anchor="start", fill=MUTED)
    s.path("M 92 140 Q 150 100 208 140", stroke=ORANGE, width=2)
    s.text(150, 115, "super() in B", size=11, fill=ORANGE, weight="bold")
    s.text(420, 190, "super() means the next class in the", size=12, anchor="start")
    s.text(420, 208, "MRO of the object, so inside B it is C,", size=12, anchor="start")
    s.text(420, 226, "the sibling, not A the parent.", size=12, anchor="start")
    s.text(420, 254, "A runs once, last, from C.", size=12, anchor="start", fill=ORANGE, weight="bold")
    s.save("05_mro_diamond.svg")


def iterator_protocol():
    s = Svg(840, 230, "A for loop calls iter once, then next until StopIteration")
    s.text(20, 30, "for x in xs:", size=14, mono=True, anchor="start", weight="bold")
    s.box(20, 60, 90, 44, "xs", sub="iterable")
    s.line(110, 82, 170, 82, stroke=BLUE)
    s.text(140, 72, "iter()", size=11, fill=BLUE, mono=True)
    s.box(175, 60, 110, 44, "iterator", fill=FILL_BLUE, sub="has __next__")
    for i, (label, val) in enumerate([("next()", "10"), ("next()", "20"), ("next()", "30")]):
        x = 330 + i * 110
        s.line(x - 45 if i else 285, 82, x, 82, stroke=GREEN)
        s.text(x - 22 if i else 307, 72, label, size=11, fill=GREEN, mono=True)
        s.rect(x, 64, 40, 36, fill=FILL_GREEN)
        s.text(x + 20, 87, val, size=13, mono=True)
        s.text(x + 20, 120, f"x = {val}", size=11, mono=True, fill=MUTED)
    s.line(700, 82, 745, 82, stroke=RED)
    s.text(722, 72, "next()", size=11, fill=RED, mono=True)
    s.text(722, 120, "StopIteration", size=11, mono=True, fill=RED)
    s.text(722, 136, "loop ends", size=11, fill=RED)
    s.text(20, 175, "A list builds a fresh iterator on every iter(), so it survives a second loop.", size=12, anchor="start", fill=MUTED)
    s.text(20, 195, "An iterator's __iter__ returns itself, so it is used up after one pass.", size=12, anchor="start", fill=MUTED)
    s.text(20, 215, "A generator function does the __next__ bookkeeping for you: each yield is one next().", size=12, anchor="start", fill=MUTED)
    s.save("08_iterator_protocol.svg")


def growth():
    import math
    s = Svg(560, 340, "Growth of step count against input size for four Big-O shapes")
    ox, oy, W, H = 60, 290, 440, 250
    s.line(ox, oy, ox + W, oy, stroke=INK)
    s.line(ox, oy, ox, oy - H, stroke=INK)
    s.text(ox + W / 2, oy + 30, "n, the input size", size=12)
    s.text(18, oy - H / 2, "steps", size=12)
    nmax, smax = 16, 64
    def px(n): return ox + n / nmax * W
    def py(v): return oy - min(v, smax) / smax * H
    for n in (4, 8, 12, 16):
        s.text(px(n), oy + 15, str(n), size=11, fill=MUTED)
    for v in (16, 32, 48, 64):
        s.text(ox - 8, py(v) + 4, str(v), size=11, fill=MUTED, anchor="end")
        s.line(ox, py(v), ox + W, py(v), stroke=MUTED, arrow=False, width=0.5, dashed=True)
    curves = [
        ("O(n²)", RED, lambda n: n * n),
        ("O(n)", ORANGE, lambda n: n),
        ("O(log n)", BLUE, lambda n: math.log2(n) if n else 0),
        ("O(1)", GREEN, lambda n: 1),
    ]
    for label, color, f in curves:
        pts = []
        for i in range(10 if label == "O(log n)" else 0, 161):
            n = i / 10
            v = f(n)
            if v > smax:
                break
            pts.append(f"{px(n):.1f},{py(v):.1f}")
        s.parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
    s.text(px(8.3) + 6, py(64) + 12, "O(n²)", size=12, fill=RED, weight="bold", anchor="start")
    s.text(px(16) + 4, py(16) + 4, "O(n)", size=12, fill=ORANGE, weight="bold", anchor="start")
    s.text(px(16) + 4, py(4) + 4, "O(log n)", size=12, fill=BLUE, weight="bold", anchor="start")
    s.text(ox + 30, py(1) - 8, "O(1)", size=12, fill=GREEN, weight="bold", anchor="start")
    s.text(ox + W / 2, 22, "Doubling n: O(n) doubles, O(n²) quadruples, O(log n) adds one step, O(1) does not move.", size=12, fill=MUTED)
    s.save("10_growth.svg")


def stack_queue():
    s = Svg(700, 260, "A stack pushes and pops at the same end; a queue joins at the back and leaves from the front")
    s.text(130, 30, "Stack  (LIFO)", size=14, weight="bold")
    for i, v in enumerate(["a", "b", "c"]):
        y = 200 - i * 40
        s.rect(90, y, 80, 36, fill=FILL_BLUE if i == 2 else "none")
        s.text(130, y + 24, v, size=14, mono=True)
    s.text(130, 250, "_items = [a, b, c]", size=11, mono=True, fill=MUTED)
    s.line(40, 125, 85, 125, stroke=GREEN)
    s.text(40, 115, "push", size=12, fill=GREEN, anchor="start")
    s.line(175, 125, 220, 125, stroke=ORANGE)
    s.text(220, 115, "pop", size=12, fill=ORANGE, anchor="end")
    s.text(130, 110, "top", size=11, fill=BLUE)
    s.text(500, 30, "Queue  (FIFO)", size=14, weight="bold")
    for i, v in enumerate(["a", "b", "c"]):
        x = 400 + i * 70
        s.rect(x, 120, 60, 40, fill=FILL_BLUE if i == 0 else "none")
        s.text(x + 30, 145, v, size=14, mono=True)
    s.text(500, 185, "front", size=11, fill=BLUE, anchor="end")
    s.text(430, 185, "", size=11)
    s.line(340, 140, 395, 140, stroke=ORANGE)
    s.text(365, 125, "dequeue", size=12, fill=ORANGE)
    s.line(620, 140, 665, 140, stroke=GREEN, arrow=True)
    s.text(640, 125, "enqueue", size=12, fill=GREEN)
    s.text(500, 220, "list.pop(0) shifts b and c left: O(n).", size=12, fill=MUTED)
    s.text(500, 240, "deque.popleft() moves nothing: O(1).", size=12, fill=MUTED)
    s.save("11_stack_queue.svg")


def node(s, x, y, val, nxt="•", fill="none", stroke=INK):
    s.rect(x, y, 96, 36, fill=fill, stroke=stroke)
    s.line(x + 52, y, x + 52, y + 36, stroke=stroke, arrow=False)
    s.text(x + 26, y + 24, str(val), size=13, mono=True)
    s.text(x + 74, y + 24, nxt, size=10 if nxt == "None" else 13, mono=True, fill=MUTED)


def linked_list_ops():
    s = Svg(1000, 470, "insert_after moves two pointers; reverse walks with prev, current and next_node")
    s.text(20, 28, "insert_after(node_1, 2)", size=14, mono=True, anchor="start", weight="bold")
    node(s, 20, 50, 1)
    node(s, 260, 50, 3, "None")
    s.line(94, 68, 256, 68, stroke=MUTED, arrow=True, dashed=True)
    s.text(175, 60, "old node_1.next", size=10, fill=MUTED)
    node(s, 130, 130, 2, fill=FILL_ORANGE, stroke=ORANGE)
    s.path("M 204 148 Q 270 148 290 90", stroke=BLUE, width=2)
    s.text(380, 140, "1  new.next = node_1.next", size=12, fill=BLUE, anchor="start", mono=True)
    s.path("M 74 86 Q 74 148 126 148", stroke=ORANGE, width=2)
    s.text(380, 160, "2  node_1.next = new", size=12, fill=ORANGE, anchor="start", mono=True)
    s.text(380, 185, "Two assignments, no walking, however long the list.", size=12, fill=MUTED, anchor="start")
    s.text(380, 203, "Node(value, next) does both: node_1.next = Node(2, node_1.next)", size=11, fill=MUTED, anchor="start", mono=True)

    s.text(20, 250, "reverse()  one loop step at a time", size=14, mono=True, anchor="start", weight="bold")
    rows = [
        ("start", [("1", "→"), ("2", "→"), ("3", "None")], {"prev": None, "current": 0}, "prev = None, current = head"),
        ("after 1", [("1", "None"), ("2", "→"), ("3", "None")], {"prev": 0, "current": 1}, "1.next = prev; prev = 1; current = 2"),
        ("after 2", [("1", "None"), ("2", "←"), ("3", "None")], {"prev": 1, "current": 2}, "2.next = 1; prev = 2; current = 3"),
        ("after 3", [("1", "None"), ("2", "←"), ("3", "←")], {"prev": 2, "current": None}, "3.next = 2; prev = 3; current = None; head = prev"),
    ]
    for r, (label, cells, ptrs, caption) in enumerate(rows):
        y = 275 + r * 46
        s.text(20, y + 24, label, size=11, fill=MUTED, anchor="start")
        for i, (val, nxt) in enumerate(cells):
            x = 90 + i * 122
            fill = FILL_BLUE if ptrs["current"] == i else (FILL_GREEN if ptrs["prev"] == i else "none")
            node(s, x, y, val, nxt, fill=fill)
            if nxt == "→":
                s.line(x + 96, y + 18, x + 118, y + 18, stroke=INK)
            elif nxt == "←" and i > 0:
                s.line(x - 3, y + 30, x - 24, y + 30, stroke=GREEN, width=2)
        s.text(470, y + 22, caption, size=11, mono=True, anchor="start")
    s.rect(90, 460, 12, 8, fill=FILL_GREEN, stroke=GREEN)
    s.text(108, 467, "prev", size=10, anchor="start", fill=MUTED)
    s.rect(150, 460, 12, 8, fill=FILL_BLUE, stroke=BLUE)
    s.text(168, 467, "current", size=10, anchor="start", fill=MUTED)
    s.text(300, 467, "next_node is saved before current.next is turned around, or the rest of the list is lost.", size=10, anchor="start", fill=MUTED)
    s.save("12_linked_list_ops.svg")


def call_stack():
    s = Svg(700, 300, "factorial(3) pushes four frames, then each returns into the one below")
    s.text(150, 28, "frames pushed", size=13, weight="bold")
    s.text(520, 28, "frames popped, top first", size=13, weight="bold")
    frames = ["factorial(3)", "factorial(2)", "factorial(1)", "factorial(0)"]
    for i, f in enumerate(frames):
        y = 220 - i * 50
        top = i == 3
        s.rect(60, y, 180, 42, fill=FILL_YELLOW if top else "none")
        s.text(150, y + 20, f, size=13, mono=True)
        s.text(150, y + 35, "returns 1, the base case" if top else f"waiting on {3 - i} * ...", size=10, fill=MUTED)
        if i < 3:
            s.line(150, y - 2, 150, y - 6, stroke=BLUE, arrow=True)
            s.text(255, y - 10, f"calls factorial({2 - i})", size=11, fill=BLUE, anchor="start")
    returns = ["6", "2", "1", "1"]
    for i, f in enumerate(frames):
        y = 220 - i * 50
        s.rect(430, y, 180, 42, fill=FILL_GREEN)
        s.text(520, y + 20, f, size=13, mono=True)
        s.text(520, y + 35, "base case: 1" if i == 3 else f"{3 - i} * {returns[i + 1]} = {returns[i]}", size=10, fill=GREEN)
        if i > 0:
            s.line(520, y + 46, 520, y + 50 + 2, stroke=GREEN, arrow=True)
            s.text(625, y + 52, f"returns {returns[i]}", size=11, fill=GREEN, anchor="start")
    s.text(350, 288, "Every frame has its own n. The stack grows to the base case, then unwinds. About 1000 frames and Python raises RecursionError.", size=11, fill=MUTED)
    s.save("13_call_stack.svg")


def merge_sort():
    s = Svg(760, 425, "Merge sort splits down to single items and merges sorted halves back up")
    def row(y, lists, fill, color):
        total = sum(len(l) for l in lists)
        gap = 22
        cell = (720 - gap * (len(lists) - 1)) / total
        x = 20
        for l in lists:
            for v in l:
                s.rect(x, y, cell - 2, 30, fill=fill, stroke=color, rx=3)
                s.text(x + (cell - 2) / 2, y + 20, str(v), size=13, mono=True)
                x += cell
            x += gap
    s.text(20, 22, "split", size=12, fill=BLUE, weight="bold", anchor="start")
    row(30, [[5, 2, 4, 6, 1, 3]], "none", INK)
    row(85, [[5, 2, 4], [6, 1, 3]], "none", BLUE)
    row(140, [[5], [2, 4], [6], [1, 3]], "none", BLUE)
    row(195, [[5], [2], [4], [6], [1], [3]], FILL_YELLOW, INK)
    s.text(20, 245, "merge", size=12, fill=GREEN, weight="bold", anchor="start")
    row(255, [[5], [2, 4], [6], [1, 3]], FILL_GREEN, GREEN)
    row(310, [[2, 4, 5], [1, 3, 6]], FILL_GREEN, GREEN)
    row(365, [[1, 2, 3, 4, 5, 6]], FILL_GREEN, GREEN)
    for y in (62, 117, 172):
        s.line(380, y, 380, y + 20, stroke=BLUE)
    for y in (227, 282, 337):
        s.line(380, y, 380, y + 20, stroke=GREEN)
    s.text(600, 22, "length 0 or 1 is already sorted", size=11, fill=MUTED)
    s.text(600, 245, "merge takes the smaller front item each time", size=11, fill=MUTED)
    s.text(740, 415, "log2(n) levels, n work each: O(n log n)", size=11, fill=MUTED, anchor="end")
    s.save("14_merge_sort.svg")


def binary_search():
    s = Svg(700, 230, "Binary search for 7 halves the sorted list at each step")
    items = [1, 3, 5, 7, 9, 11, 13]
    steps = [
        (0, 6, 3, "items[3] is 7: found at index 3", GREEN),
    ]
    steps = [
        (0, 6, 3, "mid = 3, items[3] = 7 = target: return 3", GREEN),
    ]
    target = 10
    steps = [
        (0, 6, 3, "mid = 3, 7 < 10: lo = 4", BLUE),
        (4, 6, 5, "mid = 5, 11 > 10: hi = 4", BLUE),
        (4, 4, 4, "mid = 4, 9 < 10: lo = 5", BLUE),
        (5, 4, None, "lo > hi: return -1", RED),
    ]
    s.text(20, 24, "target = 10", size=13, mono=True, anchor="start", weight="bold")
    for r, (lo, hi, mid, caption, color) in enumerate(steps):
        y = 40 + r * 46
        for i, v in enumerate(items):
            x = 20 + i * 50
            alive = lo <= i <= hi
            fill = FILL_BLUE if i == mid else ("none" if alive else FILL_GREY)
            s.rect(x, y, 44, 30, fill=fill, stroke=INK if alive else MUTED, rx=3)
            s.text(x + 22, y + 20, str(v), size=13, mono=True, fill=INK if alive else MUTED)
        if lo < hi:
            s.text(20 + lo * 50 + 22, y + 42, "lo", size=10, fill=BLUE)
            s.text(20 + hi * 50 + 22, y + 42, "hi", size=10, fill=BLUE)
        elif lo == hi:
            s.text(20 + lo * 50 + 22, y + 42, "lo = hi", size=10, fill=BLUE)
        s.text(390, y + 20, caption, size=12, mono=True, anchor="start", fill=color)
    s.text(20, 222, "Each step discards half of what is left: about log2(n) looks. For a million items that is 20.", size=11, fill=MUTED, anchor="start")
    s.save("14_binary_search.svg")


def hash_buckets():
    s = Svg(760, 300, "A key is hashed, reduced modulo the bucket count, and found by walking one bucket")
    s.box(20, 40, 80, 40, '"emu"', fill=FILL_YELLOW)
    s.line(100, 60, 150, 60, stroke=BLUE)
    s.text(125, 50, "hash()", size=11, fill=BLUE, mono=True)
    s.box(150, 40, 110, 40, "8 273 190", sub="an int")
    s.line(260, 60, 310, 60, stroke=BLUE)
    s.text(285, 50, "% 4", size=11, fill=BLUE, mono=True)
    s.box(310, 40, 60, 40, "2", fill=FILL_BLUE, sub="bucket")
    buckets = [
        [("dog", 1)],
        [],
        [("cat", 2), ("emu", 3)],
        [],
    ]
    for i, b in enumerate(buckets):
        y = 110 + i * 42
        s.text(430, y + 24, str(i), size=13, mono=True, fill=MUTED)
        s.rect(460, y, 280, 36, fill=FILL_BLUE if i == 2 else "none", stroke=BLUE if i == 2 else MUTED)
        x = 470
        for key, val in b:
            hit = key == "emu"
            s.rect(x, y + 5, 100, 26, fill=FILL_GREEN if hit else "none", stroke=GREEN if hit else INK, rx=3)
            s.text(x + 50, y + 23, f'["{key}", {val}]', size=11, mono=True)
            x += 110
    s.path("M 340 80 Q 340 200 458 200", stroke=BLUE, width=2)
    s.text(20, 262, "get walks bucket 2 comparing keys with ==", size=12, anchor="start", fill=BLUE)
    s.text(600, 100, "buckets", size=11, fill=MUTED)
    s.text(20, 140, "Two keys in one bucket is a collision.", size=12, anchor="start")
    s.text(20, 158, "Buckets stay short, so the walk is a", size=12, anchor="start")
    s.text(20, 176, "few steps: O(1) on average.", size=12, anchor="start")
    s.text(20, 210, "When pairs outnumber buckets, double", size=12, anchor="start")
    s.text(20, 228, "the buckets and re-place every pair.", size=12, anchor="start")
    s.text(20, 284, "__hash__ picks the bucket, __eq__ finds the key inside it. They must agree or the key is never found.", size=11, fill=MUTED, anchor="start")
    s.save("15_hash_buckets.svg")


def tree_at(s, ox, oy, order, color, fill):
    pos = {8: (0, 0), 3: (-50, 55), 10: (50, 55), 1: (-80, 110), 6: (-20, 110), 14: (80, 110)}
    edges = [(8, 3), (8, 10), (3, 1), (3, 6), (10, 14)]
    for a, b in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        s.line(ox + x1, oy + y1, ox + x2, oy + y2, stroke=MUTED, arrow=False)
    for v, (x, y) in pos.items():
        s.circle(ox + x, oy + y, 16, fill=fill)
        s.text(ox + x, oy + y + 5, str(v), size=12, mono=True)
        s.circle(ox + x + 15, oy + y - 13, 9, fill=color, stroke=color)
        s.text(ox + x + 15, oy + y - 9, str(order.index(v) + 1), size=10, fill="#ffffff", weight="bold")


def traversals():
    s = Svg(940, 240, "The same tree visited in four orders; the badge on each node is its visit number")
    kinds = [
        ("inorder", [1, 3, 6, 8, 10, 14], "left, node, right: sorted", BLUE),
        ("preorder", [8, 3, 1, 6, 10, 14], "node, left, right: root first", ORANGE),
        ("postorder", [1, 6, 3, 14, 10, 8], "left, right, node: root last", GREEN),
        ("level_order", [8, 3, 10, 1, 6, 14], "row by row with a queue", PURPLE),
    ]
    for i, (name, order, caption, color) in enumerate(kinds):
        ox = 115 + i * 220
        s.text(ox, 24, name, size=13, mono=True, weight="bold", fill=color)
        tree_at(s, ox, 60, order, color, BG)
        s.text(ox, 205, caption, size=11, fill=MUTED)
        s.text(ox, 225, " ".join(str(v) for v in order), size=11, mono=True)
    s.save("16_traversals.svg")


def heap():
    s = Svg(760, 330, "A heap as a tree and as the list that stores it, with one sift-down traced")
    vals = [1, 3, 2, 7, 4]
    pos = [(0, 0), (-50, 55), (50, 55), (-80, 110), (-20, 110)]
    ox, oy = 130, 50
    for i in range(1, 5):
        (x1, y1), (x2, y2) = pos[(i - 1) // 2], pos[i]
        s.line(ox + x1, oy + y1, ox + x2, oy + y2, stroke=MUTED, arrow=False)
    for i, (x, y) in enumerate(pos):
        s.circle(ox + x, oy + y, 16, fill=FILL_BLUE)
        s.text(ox + x, oy + y + 5, str(vals[i]), size=12, mono=True)
        s.text(ox + x + 22, oy + y - 10, f"i={i}", size=9, fill=MUTED, anchor="start")
    s.text(130, 195, "every parent ≤ its children", size=11, fill=MUTED)
    for i, v in enumerate(vals):
        x = 300 + i * 44
        s.rect(x, 60, 40, 32, fill=FILL_BLUE)
        s.text(x + 20, 81, str(v), size=13, mono=True)
        s.text(x + 20, 108, str(i), size=10, fill=MUTED)
    s.text(300, 45, "_items", size=11, mono=True, anchor="start", fill=MUTED)
    s.text(300, 140, "parent(i) = (i - 1) // 2", size=12, mono=True, anchor="start")
    s.text(300, 158, "left(i)   = 2 * i + 1", size=12, mono=True, anchor="start")
    s.text(300, 176, "right(i)  = 2 * i + 2", size=12, mono=True, anchor="start")
    s.path("M 452 108 Q 452 130 388 112", stroke=ORANGE, width=1.5)
    s.text(470, 120, "parent of 3 is 1", size=10, fill=ORANGE, anchor="start")
    s.text(20, 232, "_sift_down(0) on [9, 1, 2, 3, 4]", size=13, mono=True, anchor="start", weight="bold")
    rows = [([9, 1, 2, 3, 4], 0, 1, "9 > smaller child 1: swap"), ([1, 9, 2, 3, 4], 1, 3, "9 > smaller child 3: swap"), ([1, 3, 2, 9, 4], 3, None, "no child smaller: stop")]
    for r, (items, i, j, caption) in enumerate(rows):
        y = 245 + r * 30
        for k, v in enumerate(items):
            x = 60 + k * 40
            fill = FILL_ORANGE if k in (i, j) else "none"
            s.rect(x, y, 36, 24, fill=fill, stroke=ORANGE if k in (i, j) else MUTED, rx=3)
            s.text(x + 18, y + 17, str(v), size=12, mono=True)
        s.text(280, y + 17, caption, size=11, anchor="start", fill=MUTED)
    s.save("17_heap.svg")


def graph_at(s, ox, oy, order, color, title):
    pos = {"A": (0, 0), "B": (80, 0), "D": (160, 0), "C": (0, 70), "E": (80, 70), "F": (160, 70)}
    edges = [("A", "B"), ("B", "D"), ("A", "C"), ("B", "E"), ("C", "E")]
    s.text(ox + 80, oy - 35, title, size=13, mono=True, weight="bold", fill=color)
    for a, b in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        s.line(ox + x1, oy + y1, ox + x2, oy + y2, stroke=MUTED, arrow=False)
    for name, (x, y) in pos.items():
        visited = name in order
        s.circle(ox + x, oy + y, 16, fill=BG if visited else FILL_GREY, stroke=INK if visited else MUTED)
        s.text(ox + x, oy + y + 5, name, size=12, mono=True, fill=INK if visited else MUTED)
        if visited:
            s.circle(ox + x + 17, oy + y - 15, 9, fill=color, stroke=color)
            s.text(ox + x + 17, oy + y - 11, str(order.index(name) + 1), size=10, fill="#ffffff", weight="bold")
    s.text(ox + 80, oy + 110, " ".join(order), size=11, mono=True)


def bfs_dfs():
    s = Svg(760, 200, "BFS and DFS from A on the example graph; badges are visit order, F is unreachable")
    graph_at(s, 60, 60, ["A", "B", "C", "D", "E"], BLUE, "bfs('A')  deque")
    graph_at(s, 320, 60, ["A", "B", "D", "E", "C"], ORANGE, "dfs('A')  recursion")
    s.text(580, 50, "BFS: one step away, then two,", size=12, anchor="start")
    s.text(580, 68, "so the first time it reaches a", size=12, anchor="start")
    s.text(580, 86, "node is by a shortest path.", size=12, anchor="start")
    s.text(580, 116, "DFS: follow one path to its end,", size=12, anchor="start")
    s.text(580, 134, "then back up and try the next.", size=12, anchor="start")
    s.text(580, 164, "Both keep a seen set; without it", size=12, anchor="start", fill=MUTED)
    s.text(580, 182, "the cycle A B E C A never ends.", size=12, anchor="start", fill=MUTED)
    s.save("18_bfs_dfs.svg")


def dijkstra():
    s = Svg(800, 250, "Dijkstra relaxes the cheapest known node first; the route via C beats the direct edge to B")
    pos = {"A": (60, 120), "B": (260, 60), "C": (260, 180), "D": (460, 120)}
    edges = [("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5)]
    for a, b, w in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        on_path = (a, b) in [("A", "C"), ("C", "B"), ("B", "D")]
        s.line(x1, y1, x2, y2, stroke=GREEN if on_path else MUTED, arrow=False, width=2.5 if on_path else 1.5)
        s.text((x1 + x2) / 2 + 8, (y1 + y2) / 2 - 6, str(w), size=12, fill=INK, anchor="start", mono=True)
    dist = {"A": "0", "B": "4 → 3", "C": "1", "D": "8"}
    for name, (x, y) in pos.items():
        s.circle(x, y, 18, fill=FILL_GREEN)
        s.text(x, y + 5, name, size=13, mono=True)
        if name == "B":
            s.text(x - 30, y - 28, "dist 4 → 3", size=11, fill=GREEN, mono=True, anchor="end")
        else:
            s.text(x, y + 38, f"dist {dist[name]}", size=11, fill=MUTED, mono=True)
    s.text(530, 60, "heap of (distance, node)", size=12, anchor="start", weight="bold")
    s.text(530, 82, "pop (0, A): B=4, C=1", size=11, anchor="start", mono=True)
    s.text(530, 100, "pop (1, C): B=1+2=3 beats 4", size=11, anchor="start", mono=True, fill=GREEN)
    s.text(530, 118, "pop (3, B): D=8", size=11, anchor="start", mono=True)
    s.text(530, 136, "pop (4, B): stale, skip", size=11, anchor="start", mono=True, fill=MUTED)
    s.text(530, 154, "pop (8, D): done", size=11, anchor="start", mono=True)
    s.text(400, 235, "A node's distance is final when it is popped, because every entry still in the heap costs at least as much.", size=11, fill=MUTED)
    s.save("18_dijkstra.svg")


def fib_overlap():
    s = Svg(1000, 300, "fib(5) computes fib(3) twice and fib(2) three times; memoisation keeps one of each")
    def draw(n, x, y, spread):
        fill = {3: FILL_ORANGE, 2: FILL_BLUE}.get(n, "none")
        stroke = {3: ORANGE, 2: BLUE}.get(n, INK)
        if n < 2:
            fill, stroke = FILL_GREY, MUTED
        s.circle(x, y, 17, fill=fill, stroke=stroke)
        s.text(x, y + 4, f"f{n}", size=11, mono=True)
        if n >= 2:
            for child, dx in ((n - 1, -spread), (n - 2, spread)):
                s.line(x, y + 17, x + dx, y + 60 - 17, stroke=MUTED, arrow=False)
                draw(child, x + dx, y + 60, spread / 2)
    draw(5, 330, 30, 160)
    s.text(660, 60, "fib(3) is the orange subtree,", size=12, anchor="start")
    s.text(660, 78, "computed twice.", size=12, anchor="start", fill=ORANGE)
    s.text(660, 106, "fib(2) is the blue subtree,", size=12, anchor="start")
    s.text(660, 124, "computed three times.", size=12, anchor="start", fill=BLUE)
    s.text(660, 160, "With a memo dict each subtree", size=12, anchor="start")
    s.text(660, 178, "runs once; later asks return", size=12, anchor="start")
    s.text(660, 196, "from the dict. 15 calls become 9.", size=12, anchor="start", weight="bold")
    s.text(660, 232, "A table fills fib(0), fib(1), ... up", size=12, anchor="start", fill=MUTED)
    s.text(660, 250, "to fib(n) with no recursion at all.", size=12, anchor="start", fill=MUTED)
    s.save("19_fib_overlap.svg")


def lcs_grid():
    s = Svg(560, 330, "The LCS table for abcde and ace: diagonal + 1 on a match, else the larger of up and left")
    a, b = "abcde", "ace"
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    ox, oy, c = 100, 60, 44
    for j in range(len(b) + 1):
        s.text(ox + j * c + c / 2, oy - 12, '""' if j == 0 else b[j - 1], size=13, mono=True, fill=MUTED)
    for i in range(len(a) + 1):
        s.text(ox - 14, oy + i * c + c / 2 + 5, '""' if i == 0 else a[i - 1], size=13, mono=True, fill=MUTED, anchor="end")
        for j in range(len(b) + 1):
            match = i > 0 and j > 0 and a[i - 1] == b[j - 1]
            fill = FILL_GREEN if match else ("none" if i and j else FILL_GREY)
            s.rect(ox + j * c, oy + i * c, c - 2, c - 2, fill=fill, stroke=GREEN if match else MUTED, rx=3)
            s.text(ox + j * c + c / 2, oy + i * c + c / 2 + 5, str(table[i][j]), size=13, mono=True)
    for (i, j) in [(1, 1), (3, 2), (5, 3)]:
        x1, y1 = ox + (j - 1) * c + c / 2 + 12, oy + (i - 1) * c + c / 2 + 12
        s.line(x1, y1, x1 + 14, y1 + 14, stroke=GREEN, width=2)
    s.text(300, 80, "match: diagonal + 1", size=12, anchor="start", fill=GREEN, weight="bold")
    s.text(300, 100, "else:  max(up, left)", size=12, anchor="start")
    s.text(300, 130, "Row 0 and column 0 are the", size=12, anchor="start", fill=MUTED)
    s.text(300, 148, "empty prefix: nothing shared.", size=12, anchor="start", fill=MUTED)
    s.text(300, 180, "Each cell is the answer for two", size=12, anchor="start")
    s.text(300, 198, "prefixes, so the bottom-right", size=12, anchor="start")
    s.text(300, 216, "cell is the answer for the whole.", size=12, anchor="start")
    s.text(300, 250, f"lcs('abcde', 'ace') = {table[-1][-1]}", size=13, anchor="start", mono=True, weight="bold")
    s.save("19_lcs_grid.svg")


def race_interleaving():
    s = Svg(700, 320, "Two threads each read, add one and write a shared counter; interleaved, one increment is lost")
    s.text(150, 28, "thread A", size=14, weight="bold", fill=BLUE)
    s.text(400, 28, "thread B", size=14, weight="bold", fill=ORANGE)
    s.text(600, 28, "count", size=14, weight="bold")
    steps = [
        (150, "n = count", "reads 0", BLUE, FILL_BLUE, "0"),
        (400, "n = count", "reads 0 too", ORANGE, FILL_ORANGE, "0"),
        (150, "count = n + 1", "writes 1", BLUE, FILL_BLUE, "1"),
        (400, "count = n + 1", "writes 1 again", ORANGE, FILL_ORANGE, "1"),
    ]
    for i, (x, label, sub, color, fill, value) in enumerate(steps):
        y = 50 + i * 56
        s.box(x - 90, y, 180, 42, label, fill=fill, stroke=color, sub=sub)
        s.rect(570, y, 60, 42, fill=FILL_RED if i == 3 else "none")
        s.text(600, y + 26, value, size=15, mono=True)
        if i < 3:
            s.line(600, y + 44, 600, y + 54, stroke=INK, arrow=False, dashed=True)
    s.line(60, 60, 60, 260, stroke=MUTED, arrow=True)
    s.text(60, 275, "time", size=11, fill=MUTED)
    s.text(600, 290, "two increments, count is 1", size=12, fill=RED)
    s.text(275, 295, "with lock: B cannot read until A has written, so B reads 1 and writes 2.", size=12, fill=MUTED)
    s.save("22_race_interleaving.svg")


def event_loop():
    s = Svg(700, 320, "One event loop runs two tasks; each await hands control back and the loop resumes the task later")
    s.box(250, 20, 200, 44, "event loop", fill=FILL_YELLOW, mono=False, size=14, sub="one thread, one task at a time")
    s.text(240, 46, "await hands control back", size=11, fill=MUTED, anchor="end")
    s.text(460, 46, "the loop resumes it later", size=11, fill=MUTED, anchor="start")
    lanes = [("task a", 120, BLUE, FILL_BLUE, 320, 420), ("task b", 230, ORANGE, FILL_ORANGE, 262, 448)]
    for name, y, color, fill, up_x, down_x in lanes:
        s.text(40, y + 25, name, size=13, weight="bold", fill=color, anchor="start")
        s.box(110, y, 110, 40, "run", fill=fill, stroke=color, mono=False)
        s.rect(300, y, 130, 40, stroke=color, dashed=True)
        s.text(365, y + 24, "await sleep()", size=12, mono=True, fill=color)
        s.box(510, y, 110, 40, "resume", fill=fill, stroke=color, mono=False)
        s.line(222, y + 20, 298, y + 20, stroke=color, arrow=True)
        s.line(432, y + 20, 508, y + 20, stroke=color, arrow=True)
        s.line(300, y - 2, up_x, 66, stroke=color, arrow=True, dashed=True)
        s.line(down_x, 66, 430, y - 2, stroke=color, arrow=True, dashed=True)
    s.text(350, 300, "a runs and awaits, b runs and awaits, the loop resumes whichever wakes first. time.sleep() never hands back, so everything waits.", size=11, fill=MUTED)
    s.save("24_event_loop.svg")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for draw in (
        attribute_lookup, mro_diamond, iterator_protocol, growth, stack_queue, linked_list_ops,
        call_stack, merge_sort, binary_search, hash_buckets, traversals, heap, bfs_dfs, dijkstra,
        fib_overlap, lcs_grid, race_interleaving, event_loop,
    ):
        draw()


if __name__ == "__main__":
    main()
