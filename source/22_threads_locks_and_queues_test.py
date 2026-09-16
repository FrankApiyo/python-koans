"""Threads, locks, and queues.

A thread is a second line of execution inside the same program. It shares
every object with the thread that started it, so a list appended from one
thread is visible in the other. threading.Thread(target=f) makes one,
start() begins running f alongside your own code, and join() waits for it
to finish. The thread you begin in is called MainThread.

    t = threading.Thread(target=work)
    t.start()      # work is now running alongside this line
    t.join()       # wait here until it is done

Sharing is the danger. counter += 1 is really three steps: read the value,
add one, write it back. If two threads both read 0 before either writes,
both write 1 and one increment is lost. That is a race. A Lock lets one
thread at a time through a block; with lock: acquires it before the block
and releases it after, even if the block raises, exactly like the context
managers of chapter 09. An RLock is a lock the same thread may take twice.

Python's interpreter holds a global interpreter lock, the GIL, so only one
thread runs Python code at any instant. Threads still help when the work is
waiting: for a network reply, for a file, for time.sleep, because a waiting
thread lets go of the GIL. They do not make pure arithmetic faster; for
that, chapter 23 reaches for processes.

queue.Queue is the safe way for threads to hand each other work. It is the
FIFO queue of chapter 11 with the locking built in: put adds at the back,
get takes from the front and waits if nothing is there. A producer puts
items and finally a sentinel, None, that tells the consumer to stop. Each
consumer calls task_done for every item it took, and queue.join() waits
until every item put has been marked done.

Picture: lessons/svg/22_race_interleaving.svg. Every chapter is also on lessons/index.html.
"""

import queue
import sys
import threading
import time

import pytest

from conftest import __


def unsafe_increment(shared):
    """Read, pause, write. The pause makes the race certain instead of rare."""
    current = shared["count"]
    time.sleep(0.01)
    shared["count"] = current + 1


class Counter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        # >>> answer
        with self._lock:
            current = self.value
            time.sleep(0.001)
            self.value = current + 1
        # <<<


def worker(tasks, results):
    # >>> answer
    while True:
        item = tasks.get()
        if item is None:
            tasks.task_done()
            return
        results.append(item * 2)
        tasks.task_done()
    # <<<


def consume(tasks, results):
    """A finished worker, given so the last koan does not depend on yours."""
    while True:
        item = tasks.get()
        if item is None:
            tasks.task_done()
            return
        results.append(item * 2)
        tasks.task_done()


def run_threads(count, target, *args):
    """daemon=True so a worker that never meets its sentinel cannot keep pytest from exiting."""
    threads = [threading.Thread(target=target, args=args, daemon=True) for _ in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=2)
    return threads


def test_a_thread_runs_a_function_and_join_waits_for_it():
    """Thread(target=f, args=(...)) makes a thread that will call f. start begins it. join returns only when f has finished, so the result is there afterwards."""
    results = []
    thread = threading.Thread(target=results.append, args=("done",))
    thread.start()
    thread.join()
    assert results == _a(["done"])
    assert thread.is_alive() is _a(False)


def test_start_returns_before_the_target_finishes():
    """start does not wait. Your code carries on while the thread sleeps, so it is alive and has appended nothing yet. join is where the waiting happens."""
    results = []

    def slow():
        time.sleep(0.05)
        results.append("done")

    thread = threading.Thread(target=slow)
    thread.start()
    assert thread.is_alive() is _a(True)
    assert results == _a([])
    thread.join()
    assert results == ["done"]


def test_threads_share_objects_and_know_their_own_names():
    """Both threads append to the one list you made. threading.current_thread().name is the name each was given; the thread you started in is MainThread."""
    names = []

    def record():
        names.append(threading.current_thread().name)

    first = threading.Thread(target=record, name="worker-1")
    second = threading.Thread(target=record, name="worker-2")
    first.start()
    first.join()
    second.start()
    second.join()
    assert names == _a(["worker-1", "worker-2"])
    assert threading.current_thread().name == _a("MainThread")


def test_two_threads_updating_one_value_lose_an_update():
    """unsafe_increment reads, pauses, then writes. Both threads read 0 during the pause, so both write 1. Two increments, one counted. That is a race."""
    shared = {"count": 0}
    run_threads(2, unsafe_increment, shared)
    assert shared["count"] == _a(1)


def test_a_lock_makes_read_and_write_one_step():
    """Implement Counter.increment above. 1. Open a block with `with self._lock:`. 2. Inside it read self.value into a local, call time.sleep(0.001) to keep the race honest, then set self.value to the local plus one. Only one thread is inside the block at a time, so no read can slip between another thread's read and write."""
    counter = Counter()
    counter.increment()
    assert counter.value == 1
    run_threads(10, counter.increment)
    assert counter.value == 11


def test_a_plain_lock_taken_twice_by_one_thread_waits_forever():
    """acquire(timeout=0.1) returns False when the lock could not be had. A Lock does not know who holds it, so the same thread asking again would block until the end of time. An RLock counts, and lets its owner back in."""
    lock = threading.Lock()
    lock.acquire()
    assert lock.acquire(timeout=0.1) is _a(False)
    lock.release()
    rlock = threading.RLock()
    rlock.acquire()
    assert rlock.acquire(timeout=0.1) is _a(True)
    rlock.release()
    rlock.release()


def test_the_interpreter_says_whether_the_gil_is_on():
    """sys._is_gil_enabled() reports it. A standard build says True: one thread runs Python at a time, so threads cannot make arithmetic faster. Free-threaded builds exist, and there this answer would differ."""
    assert sys._is_gil_enabled() is _a(True)


def test_threads_that_wait_do_overlap():
    """Five threads each sleep 0.1 s. Run one after another that is 0.5 s. A sleeping thread releases the GIL, so they sleep at the same time and the whole thing takes about 0.1 s. The bound is loose on purpose."""
    started = time.perf_counter()
    run_threads(5, time.sleep, 0.1)
    elapsed = time.perf_counter() - started
    assert 5 * 0.1 == _a(0.5)
    assert (elapsed < 0.4) is _a(True)


def test_a_queue_is_fifo_and_get_waits_when_empty():
    """put adds at the back and get takes from the front, first in first out. get on an empty queue blocks; with a timeout it gives up by raising queue.Empty instead of returning None."""
    tasks = queue.Queue()
    tasks.put(1)
    tasks.put(2)
    assert tasks.get() == _a(1)
    tasks.get()
    with pytest.raises(_a(queue.Empty)):
        tasks.get(timeout=0.05)


def test_a_worker_takes_items_until_it_meets_the_sentinel():
    """Implement worker above. 1. Loop forever: take item = tasks.get(). 2. If item is None, call tasks.task_done() and return. 3. Otherwise append item * 2 to results and call tasks.task_done(). Here the queue is filled in advance, so the worker runs to the sentinel in this very thread."""
    tasks = queue.Queue()
    for item in [1, 2, 3, None]:
        tasks.put(item)
    results = []
    worker(tasks, results)
    assert results == [2, 4, 6]
    assert tasks.empty() is True


def test_two_workers_share_one_queue_and_each_needs_its_own_sentinel():
    """Each get hands an item to exactly one worker, so the two split the work between them and the order of results depends on who was faster. A worker stops when it takes a None, so two workers need two."""
    tasks = queue.Queue()
    for item in [1, 2, 3, 4, 5, 6, None, None]:
        tasks.put(item)
    results = []
    threads = run_threads(2, worker, tasks, results)
    assert sorted(results) == _a([2, 4, 6, 8, 10, 12])
    assert any(thread.is_alive() for thread in threads) is _a(False)


def test_queue_join_waits_until_every_item_is_marked_done():
    """unfinished_tasks counts puts minus task_done calls. queue.join() blocks until it reaches 0, which is how a producer knows the work is finished without joining the threads. The sentinel goes in afterwards to let the worker go home."""
    tasks = queue.Queue()
    results = []
    consumer = threading.Thread(target=consume, args=(tasks, results), daemon=True)
    consumer.start()
    for item in [1, 2, 3]:
        tasks.put(item)
    tasks.join()
    pending_after_join = tasks.unfinished_tasks
    seen_after_join = list(results)
    tasks.put(None)
    consumer.join()
    assert pending_after_join == _a(0)
    assert seen_after_join == _a([2, 4, 6])
