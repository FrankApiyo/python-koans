"""Executors and futures.

Chapter 22 started threads by hand: make a Thread, start it, join it, keep
your own list of results. concurrent.futures does that bookkeeping. An
executor owns a pool of workers. You hand it callables, and it hands you a
Future for each one at once, before the work is done.

    with ThreadPoolExecutor(max_workers=4) as pool:
        future = pool.submit(slow_double, 21)
        future.result()                # waits, then returns 42

A Future is a promise of a result. done() asks whether the result has
arrived. result() waits for it and returns it, and if the callable raised,
result() raises that same exception again in your thread. exception()
hands the exception back without raising it. result(timeout=0) raises
TimeoutError instead of waiting.

Two ways to run many. pool.map(fn, items) runs fn on every item and returns
the results in the order of the items, whatever order they finished in.
as_completed(futures) yields each future the moment it finishes, so the
fastest comes first. Leaving the with block calls shutdown(wait=True): every
submitted task runs to the end first, and submitting after that raises
RuntimeError.

max_workers caps how many tasks run at once; the rest queue inside the
executor. A ThreadPoolExecutor shares one interpreter, so because of the
GIL from chapter 22 it helps work that waits and not work that computes. A
ProcessPoolExecutor has the same API but starts separate Python processes,
each with its own GIL, so computing in parallel really is parallel. The cost
is that arguments and results travel between processes as pickled bytes,
and only functions defined at module level can make the trip.

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

import math
import os
import threading
import time
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor, as_completed

import pytest

from conftest import __


def slow_double(n, delay=0.05):
    time.sleep(delay)
    return n * 2


def explode():
    raise ValueError("boom")


def wait_then_double(gate, n):
    gate.wait(timeout=5)
    return n * 2


class Gauge:
    """Counts how many workers are inside a with block at once. peak is the
    most that were ever inside together."""

    def __init__(self):
        self._lock = threading.Lock()
        self.current = 0
        self.peak = 0

    def __enter__(self):
        with self._lock:
            self.current += 1
            self.peak = max(self.peak, self.current)
        return self

    def __exit__(self, exc_type, exc, tb):
        with self._lock:
            self.current -= 1
        return False


def busy(gauge, meeting):
    with gauge:
        meeting.wait(timeout=5)


def fake_fetch(url):
    time.sleep(0.01 * len(url))
    return url.upper()


def fetch_all(urls, fetch):
    with ThreadPoolExecutor() as pool:
        return list(pool.map(fetch, urls))


def test_submit_returns_a_future_before_the_work_is_done():
    """submit hands the callable to a worker and comes straight back with a Future. The worker is parked on gate.wait(), so done() is False until the gate opens and you wait for the result."""
    gate = threading.Event()
    with ThreadPoolExecutor(max_workers=2) as pool:
        future = pool.submit(wait_then_double, gate, 21)
        assert isinstance(future, Future)
        assert future.done() is False
        gate.set()
        assert future.result() == 42
        assert future.done() is True


def test_result_waits_and_a_zero_timeout_refuses_to():
    """result() blocks your thread until the worker finishes, so the log is filled by the time it returns. result(timeout=0) will not wait at all and raises instead."""
    gate = threading.Event()
    log = []

    def work():
        gate.wait(timeout=5)
        log.append("worked")
        return "done"

    with ThreadPoolExecutor(max_workers=2) as pool:
        future = pool.submit(work)
        try:
            future.result(timeout=0)
        except Exception as error:
            refused = error
        gate.set()
        assert isinstance(refused, TimeoutError)
        assert future.result() == "done"
        assert log == ["worked"]


def test_map_returns_results_in_the_order_of_the_inputs():
    """The first input sleeps longest and finishes last, yet its result comes first. map matches results to inputs, not to finishing times."""
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(slow_double, [1, 2, 3], [0.15, 0.03, 0.09]))
    assert results == [2, 4, 6]


def test_as_completed_yields_futures_in_the_order_they_finish():
    """as_completed is for when you want each answer as soon as it exists. Three workers are parked on three gates; open them 2, 3, 1 and the futures come back in that order, whatever order they were submitted in."""
    gates = {n: threading.Event() for n in [1, 2, 3]}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(wait_then_double, gates[n], n) for n in [1, 2, 3]]
        pending = as_completed(futures)
        finished = []
        for n in [2, 3, 1]:
            gates[n].set()
            finished.append(next(pending).result())
    assert finished == [4, 6, 2]


def test_an_exception_in_a_task_is_stored_until_you_ask_for_the_result():
    """The worker thread does not crash and nothing is printed. The exception is kept inside the Future: exception() returns it, result() raises it in your thread."""
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(explode)
    assert isinstance(future.exception(), ValueError) is True
    with pytest.raises(ValueError):
        future.result()


def test_leaving_the_with_block_waits_for_every_task_then_closes_the_pool():
    """__exit__ calls shutdown(wait=True). Nothing after the with runs until all three sleeps are over, and the closed pool refuses new work."""
    log = []

    def work(n):
        time.sleep(0.03)
        log.append(n)

    with ThreadPoolExecutor(max_workers=3) as pool:
        for n in [1, 2, 3]:
            pool.submit(work, n)
    assert sorted(log) == [1, 2, 3]
    with pytest.raises(RuntimeError):
        pool.submit(work, 4)


def test_max_workers_caps_how_many_run_at_once():
    """Six tasks are submitted but only two workers exist, so the rest queue up inside the executor. Each task waits at a Barrier(2), so tasks can only leave in pairs, and the Gauge, guarded by a Lock as in chapter 22, records the most that were ever inside together."""
    gauge = Gauge()
    meeting = threading.Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for _ in range(6):
            pool.submit(busy, gauge, meeting)
    assert gauge.peak == 2
    assert gauge.current == 0


def test_a_process_pool_runs_the_work_in_other_interpreters():
    """Same submit and map, but each worker is a separate Python process with its own GIL, so arithmetic in two of them is truly parallel. Arguments, results and the function itself cross by pickling, which is why the targets here are functions a worker can import by name. os.getpid inside a worker is not your pid."""
    with ProcessPoolExecutor(max_workers=2) as pool:
        factorials = list(pool.map(math.factorial, [5, 10]))
        worker_pid = pool.submit(os.getpid).result()
    assert factorials == [120, 3628800]
    assert (worker_pid == os.getpid()) is False


def test_fetch_all_fans_out_and_keeps_the_order_of_the_urls():
    """Implement fetch_all above. 1. Open a ThreadPoolExecutor in a with block. 2. Inside it, return list(pool.map(fetch, urls)). pool.map submits every url at once, unlike the lazy builtin map of chapter 21, and yields results in url order; list collects them, and leaving the with block shuts the pool down."""
    urls = ["ccc", "a", "bb"]
    assert fetch_all(urls, fake_fetch) == ["CCC", "A", "BB"]
    assert fetch_all([], fake_fetch) == []
