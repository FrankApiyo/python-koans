"""Generator pipelines.

Chapter 08 showed that a generator runs only when asked. That laziness is
worth more than saving memory: it lets you chain small stages into a
pipeline, where each stage is a generator that takes an iterable and yields
its own values, and one item flows all the way through before the next is
read from the source.

    def strip(lines):
        for line in lines:
            yield line.strip()

    def errors(lines):
        for line in lines:
            if line.startswith("ERROR"):
                yield line

    count = sum(1 for _ in errors(strip(open(path))))

Nothing here holds the file in memory. open() returns an iterator over
lines, strip pulls one line at a time, errors pulls from strip, and sum
pulls from errors. Ten lines or ten million lines cost the same memory.

The standard library supplies stages. map(f, xs) and filter(f, xs) return
lazy iterators, not lists. itertools has chain to join sources end to end,
islice and takewhile to stop early, and groupby to split runs of equal
keys. Because every stage is lazy, an infinite source is fine as long as
some later stage stops.

Two more things a generator can do. gen.send(value) resumes it and makes
the paused yield expression evaluate to value, so a stage can accept input;
a fresh generator must be started with next() or send(None) before it
can be sent a value. gen.close()
raises GeneratorExit at the paused yield, so a finally block around the
yield runs even when the consumer stops early.

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

from itertools import chain, groupby, islice, takewhile

import pytest

from conftest import __


class Pipeline:
    """A source wrapped so that stages attach with |. A stage is any function
    that takes an iterable and returns an iterable, usually a generator."""

    def __init__(self, source):
        self._source = source

    def __or__(self, stage):
        __()

    def __iter__(self):
        __()


def doubled(xs):
    for x in xs:
        yield x * 2


def only_even(xs):
    for x in xs:
        if x % 2 == 0:
            yield x


def naturals():
    n = 1
    while True:
        yield n
        n += 1


def test_a_stage_is_a_generator_that_takes_an_iterable_and_yields_its_own():
    """doubled accepts anything iterable, including the output of another stage, so stages nest like function calls and read inside out."""
    assert list(doubled([1, 2, 3])) == __
    assert list(doubled(only_even(range(7)))) == __


def test_one_item_flows_through_every_stage_before_the_next_is_read():
    """The last stage pulls one value, which pulls one value from the stage before it, all the way back to the source. Nothing waits for a whole list to be built."""
    log = []

    def first(xs):
        for x in xs:
            log.append(f"first {x}")
            yield x

    def second(xs):
        for x in xs:
            log.append(f"second {x}")
            yield x

    list(second(first([1, 2])))
    assert log == __


def test_a_pipeline_over_ten_million_numbers_never_builds_a_list():
    """range is lazy, the stages are lazy, and sum consumes one value at a time, so the peak memory is one integer no matter how long the range. Stop early with next and only the values before the answer are ever produced."""
    evens = only_even(range(10_000_000))
    assert sum(islice(evens, 5)) == __
    first_big_square = next(x for x in range(10_000_000) if x * x > 1_000_000)
    assert first_big_square == __


def test_chain_joins_sources_and_islice_or_takewhile_stops_them():
    """chain reads its second source only after the first is exhausted. naturals never ends, so a stopping stage must come later in the line: islice counts, takewhile watches a condition."""
    assert list(chain([1, 2], "ab")) == __
    assert list(takewhile(lambda n: n * n < 20, naturals())) == __


def test_map_and_filter_are_lazy_stages_too():
    """Neither runs anything until a consumer pulls. The log proves the function was not called when map was built, and that filter pulled from map one item at a time."""
    seen = []

    def square(x):
        seen.append(x)
        return x * x

    stage = filter(lambda n: n > 4, map(square, [1, 2, 3, 4]))
    assert seen == __
    assert next(stage) == __
    assert seen == [1, 2, 3]


def test_groupby_groups_runs_of_equal_keys_not_all_equal_keys():
    """groupby starts a new group each time the key changes, so a repeats. Sort by the same key first if you want one group per key."""
    runs = [(key, len(list(group))) for key, group in groupby("aabba")]
    assert runs == __
    merged = [(key, len(list(group))) for key, group in groupby(sorted("aabba"))]
    assert merged == __


def test_a_file_flows_through_the_pipeline_one_line_at_a_time(tmp_path):
    """A file object is an iterator over its lines, so it is a source like any other. counted proves how many lines were pulled: exactly enough to reach the first ERROR, not the whole file."""
    path = tmp_path / "app.log"
    path.write_text("".join(f"{'ERROR' if n % 100 == 99 else 'INFO'} event {n}\n" for n in range(10_000)))
    pulled = []

    def counted(lines):
        for line in lines:
            pulled.append(line)
            yield line

    def stripped(lines):
        for line in lines:
            yield line.strip()

    def errors(lines):
        for line in lines:
            if line.startswith("ERROR"):
                yield line

    with open(path) as handle:
        first = next(errors(stripped(counted(handle))))
        assert first == __
        assert len(pulled) == __
    with open(path) as handle:
        assert sum(1 for _ in errors(stripped(handle))) == 100


def test_send_pushes_a_value_into_a_paused_generator():
    """A yield used as an expression receives what send passes in. The first next runs to the first yield with nothing to receive, which is called priming."""

    def running_total():
        total = 0
        while True:
            received = yield total
            total += received

    gen = running_total()
    assert next(gen) == __
    gen.send(5)
    assert gen.send(10) == __


def test_close_runs_the_finally_of_a_paused_generator():
    """close raises GeneratorExit inside the generator at its paused yield. A finally around the yield is how a stage releases a file or a connection when the consumer stops early."""
    events = []

    def watched():
        try:
            yield 1
            yield 2
        finally:
            events.append("closed")

    gen = watched()
    next(gen)
    assert events == __
    gen.close()
    assert events == __


def test_or_attaches_a_stage_and_returns_a_new_pipeline():
    """Implement Pipeline.__or__ above. 1. Return a new Pipeline whose source is stage called with self._source. The | operator calls __or__ from chapter 02, so Pipeline(xs) | doubled | only_even reads left to right, and each stage is a lazy generator over the one before."""
    pipeline = Pipeline(range(5)) | doubled | only_even
    assert isinstance(pipeline, Pipeline)
    assert list(pipeline._source) == [0, 2, 4, 6, 8]


def test_iter_hands_out_the_source_so_the_pipeline_stays_lazy():
    """Implement Pipeline.__iter__ above. 1. Return iter(self._source). The pipeline is then a plain iterable, and nothing in any stage runs until a consumer pulls, which the log proves."""
    log = []

    def noted(xs):
        for x in xs:
            log.append(x)
            yield x

    pipeline = Pipeline([1, 2, 3]) | noted | doubled
    assert log == []
    assert next(iter(pipeline)) == 2
    assert log == [1]
    assert list(pipeline) == [4, 6]
