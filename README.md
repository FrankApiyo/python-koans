# Python koans

Koans for Python, in three parts. The first is object-oriented
programming, from `class` and `self` through dunder methods, properties,
inheritance, abstract classes, dataclasses, and iterators. The second is
data structures and algorithms: stacks, linked lists, recursion, sorting,
hash maps, trees, heaps, graphs, and dynamic programming. The third is
streams and concurrency: files, generator pipelines, threads, executors,
and asyncio through to sockets, ending with how such code is tested with
mocks and patches. Every file in
`koans/` is a chain of tiny tests with a blank in each one. Fill the blank,
run, read the next meditation. When every koan passes you are done, and you
can wipe the answers and go again.

There are 300 koans in 27 chapters, planned as seven mornings of two
hours, three or four chapters a morning. Nothing needs a browser or the
network; the socket koans talk to themselves on localhost. Python 3.13 or
newer is required. Each file opens with
a lesson, and each koan's meditation says what to do.

## Setup

```sh
cd python-koans
uv venv
uv pip install -r pyproject.toml
source .venv/bin/activate
nvim
```

Open nvim from this directory with the venv activated, so the test runner and
the Conjure REPL use `.venv/bin/python`. Starting in the repo root is required, because
the REPL imports the blank from `conftest.py` relative to that directory.

Do not run `uv sync`. It writes a `uv.lock`, and vim-test switches to
`uv run pytest` the moment it sees one.

## The loop

Open `koans/00_about_koans_test.py` and press `<leader>ts`. That runs the
whole suite, in order, and stops at the first koan that fails. The bottom of
the output looks like this:

```
------------------------------- The master says --------------------------------
Meditate on koans/00_about_koans_test.py:8
    Replace __ with whatever makes the assertion true, save, run again.
0 of 130 koans answered.
```

Go to that line, read the docstring above it, replace `__`, save, run again.
When the last one passes the footer changes to `Enlightenment`.

Suggested vim-test keymaps, run in a neoterm pane:

| Keys         | Runs                                           |
| ------------ | ---------------------------------------------- |
| `<leader>ts` | the whole suite, stopping at the first failure |
| `<leader>tf` | the file you are in                            |
| `<leader>tt` | the single koan under the cursor               |
| `<leader>tl` | whatever you ran last                          |

The output opens in a 15-line split at the bottom and scrolls to the end
on its own. If you ever see tests running under Homebrew's Python instead, you
started nvim somewhere other than the repo root.

## Two kinds of blank

A plain `__` stands for a value. Replace it with the number, string, list,
or whatever else makes the assertion true.

A `__()` on a line of its own stands for code. It sits where a method body
should be:

```python
class Greeter:
    def greet(self, name):
        __()
```

The meditation of the koan that exercises it says what the method must do,
step by step. Replace the whole `__()` line with the body. Until you do,
calling the method raises `NotImplementedError` and the footer points at the
blank itself, not at the assertion below it:

```
------------------------------- The master says --------------------------------
Meditate on koans/00_about_koans_test.py:34
    Implement Greeter.greet above. 1. Replace the whole __() line with a return of the string "hello " followed by name.
2 of 300 koans answered.
```

Every class you build is defined once at the top of its file. Methods you
are given are written out. Methods you must write are blanked. Each koan
exercises one method, so a linked list or a tree grows one method at a time,
and every method already written is there to lean on.

## The seven mornings

| Morning | Chapters |
| ------- | -------- |
| 1 | 00 about koans, 01 classes and instances, 02 dunder methods, 03 properties and encapsulation, 04 classmethods and staticmethods |
| 2 | 05 inheritance and MRO, 06 abstract classes and protocols, 07 dataclasses, 08 iterators and generators, 09 composition, call, and context managers |
| 3 | 10 complexity, 11 stacks and queues, 12 linked lists, 13 recursion |
| 4 | 14 searching and sorting, 15 hash maps and sets, 16 binary trees |
| 5 | 17 heaps, 18 graphs, 19 dynamic programming |
| 6 | 20 files, bytes and text, 21 generator pipelines, 22 threads, locks and queues |
| 7 | 23 executors and futures, 24 asyncio coroutines and tasks, 25 async iteration, queues and streams, 26 pytest mocks and patches |

Value koans take about a minute. Implementation koans take about five. If a
morning runs long, stop at a chapter boundary. Chapter 08 is the hinge
between the first two parts: it teaches iterators as objects, and every structure
after it is iterable because of what it taught. Chapter 21 is the second
hinge: the generators of chapter 08 become pipelines, and chapters 22 to 25
carry the same producer-and-consumer idea across threads, pools, and the
event loop. Chapter 26 closes with the tests: how a mock records a call at
the boundary and how patch swaps a name in for the length of one test.

## Pictures

`lessons/index.html` has one concise explanation per chapter and a coloured
diagram wherever a picture beats prose: attribute lookup, the MRO diamond,
the iterator protocol, Big-O growth, stacks and queues, linked list
pointer moves, the call stack, binary search, merge sort, hash buckets, tree
traversals, the heap as a list, BFS versus DFS, Dijkstra, the two
dynamic programming tables, a lost update between two threads, and the
event loop handing control back at each await. Open it once in a browser beside Neovim:

```sh
open lessons/index.html
```

Each diagram is also a standalone file under `lessons/svg/`, and the lesson
at the top of every koan file names the one it uses. If your terminal draws
images (Kitty, Ghostty, WezTerm) an image plugin such as snacks.nvim or
image.nvim can show an SVG inside Neovim; otherwise `open lessons/svg/<file>`
opens it in Preview. The diagrams are generated by `python tools/diagrams.py`.

## Trying things before you commit to an answer

The point of a koan is to know why the answer is right, not to make the test
pass. Evaluate the pieces in a REPL first.

### Conjure

Conjure's Python client starts a REPL the moment you open a Python buffer.
With the venv activated, that REPL is `.venv/bin/python`. The keys below
assume `,` as the local leader.

| Keys             | Does                                              |
| ---------------- | ------------------------------------------------- |
| `,ee`            | evaluate the call or statement under the cursor   |
| `,er`            | evaluate the enclosing top-level form             |
| `,eb`            | evaluate the whole buffer                         |
| `,E`             | evaluate a visual selection                       |
| `,lv`            | open the REPL log in a vertical split             |
| `,cS` then `,cs` | restart the REPL, for example after changing venv |

Two things to know. An `assert` line is not a form Conjure will evaluate on
its own, so `,ee` inside one re-defines the whole test function and prints
nothing. And only bare expressions print a result. So the working pattern
is:

1. `,eb` once to load the imports and helpers of the file.
2. Visually select the expression you are curious about, `stack._items` say,
   and press `,E`. Or type `:ConjureEval stack._items`.
3. Try a method call the same way until it returns what you expect.
4. Fill the blank and run the koan.

If you started nvim outside the repo and then changed directory, the REPL is
already running on the wrong Python. Restart it with `,cS` then `,cs`.

### neoterm, if you prefer ipython

`:vert Tnew` opens a terminal in a split. Then `:TREPLSendLine` on any line,
or select lines and `:'<,'>TREPLSendSelection`, sends them across. neoterm
launches ipython for you on the first send. Do not start ipython by hand
first, or the launch command gets typed into your running session.

## Starting over

```sh
git checkout -- koans/
```

That restores every blank. For one chapter:

```sh
git checkout -- 'koans/05_*'
```

Never edit `solutions/` or `source/`. If you get stuck for more than a few
minutes, the same file under `solutions/` has the answers. Read one, close it,
and write yours.

## Being stuck well

Read the lesson at the top of the file once, then read the meditation before
you read the assertion. Between the lesson, the chapters before it, and the
meditation, every koan has what it needs. For an implementation koan, write
the numbered steps of the meditation as lines of code, one step at a time,
and evaluate the object in the REPL after each step. Most confusion in the
second half is one of three things: forgetting the empty case, forgetting to
move a pointer forward, or returning inside a loop that should finish.

`solutions/` exists for after a real attempt, not instead of one.

## For maintainers

`source/` is the single authored copy. A value answer is written as
`_a(value)`. A code answer is the run of lines between a `# >>> answer` line
and a `# <<<` line, which becomes one `__()` line in `koans/`.
`python tools/generate.py` writes `koans/` and `solutions/` from it. `pytest tests/` proves every solution passes, every blank fails, and
the generated files are current.

## Licence

The code is under the Apache License 2.0 (see `LICENSE` and `NOTICE`). The lesson text,
comments that teach, pictures and README prose are under Creative Commons Attribution 4.0
(see `LICENSE-lessons`). To credit this work, write "Python koans by Frankline Apiyo" and link to
this repository.
