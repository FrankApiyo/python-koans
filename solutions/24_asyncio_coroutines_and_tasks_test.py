"""asyncio: coroutines and tasks.

A thread (chapter 22) is interrupted by the operating system whenever it
likes. A coroutine is interrupted only where it says so, at an await. That
is the whole idea of asyncio: one thread, one event loop, many coroutines
that take turns, each handing control back at its awaits.

A coroutine function is a def with async in front. Calling it runs none of
its body, exactly like calling a generator function (chapter 08). You get
a coroutine object, and something has to drive it. asyncio.run(coro)
starts an event loop, drives coro to its return value, and shuts the loop
down. Inside a coroutine, await other() drives other() right here and
pauses this coroutine until other() returns, so sequential awaits run one
after the other.

To run coroutines at the same time, wrap them in tasks. asyncio.gather(a(),
b()) makes a task of each, runs them together, and returns their results
in argument order. asyncio.create_task(coro) schedules one to start at the
next await and returns a Task you can await later, or cancel.
asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED) pauses until one
task finishes and returns two sets, done and pending.
asyncio.TaskGroup does the same inside an async with block and waits for
every task at the end; if one raises, the rest are cancelled and the errors
arrive in an ExceptionGroup. asyncio.timeout(seconds) cancels whatever is
inside it and raises TimeoutError. A cancelled task sees CancelledError at
its await.

The loop can only switch at an await. time.sleep(1) inside a coroutine is
not an await, so it freezes every task for a second. asyncio.sleep(1) is,
and lets others run meanwhile. asyncio.sleep(0) is the shortest hand-back.

Picture: lessons/svg/24_event_loop.svg. Every chapter is also on lessons/index.html.
"""

import asyncio
import inspect
import time

import pytest

from conftest import __


async def hello(log):
    log.append("ran")
    return "hi"


async def fetch(name, delay, log):
    log.append(f"start {name}")
    await asyncio.sleep(delay)
    log.append(f"end {name}")
    return name.upper()


async def blocking(log):
    log.append("start block")
    time.sleep(0.03)
    log.append("end block")


async def polite(log):
    log.append("start polite")
    await asyncio.sleep(0.03)
    log.append("end polite")


async def boom():
    await asyncio.sleep(0.01)
    raise ValueError("boom")


async def patient(log):
    try:
        await asyncio.sleep(1.0)
    except asyncio.CancelledError:
        log.append("cancelled inside")
        raise
    log.append("finished")


async def first_done(*coroutines):
    tasks = [asyncio.create_task(coro) for coro in coroutines]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    return done.pop().result()


def test_calling_a_coroutine_function_runs_nothing():
    """Like a generator, an async def hands back an object and waits to be driven. inspect.iscoroutine recognises it. close() discards it unrun."""
    log = []
    coro = hello(log)
    is_coroutine = inspect.iscoroutine(coro)
    coro.close()
    assert is_coroutine is True
    assert log == []


def test_asyncio_run_drives_a_coroutine_to_its_result():
    """asyncio.run starts a loop, runs the coroutine to its return, and stops the loop. It is the one place a plain function meets async code."""
    log = []
    assert asyncio.run(hello(log)) == "hi"
    assert log == ["ran"]


def test_fetch_logs_around_a_pause():
    """Implement fetch above. 1. Append the string "start " followed by name to log. 2. await asyncio.sleep(delay). 3. Append "end " followed by name to log. 4. Return name.upper(). The await is where this coroutine can be paused so others may run."""
    log = []
    assert asyncio.run(fetch("a", 0.01, log)) == "A"
    assert log == ["start a", "end a"]


def test_sequential_awaits_run_one_after_the_other():
    """await means wait here. The second fetch does not start until the first has returned, however short its delay."""

    async def main(log):
        a = await fetch("a", 0.02, log)
        b = await fetch("b", 0.01, log)
        return [a, b]

    log = []
    assert asyncio.run(main(log)) == ["A", "B"]
    assert log == ["start a", "end a", "start b", "end b"]


def test_gather_runs_them_together_and_keeps_argument_order():
    """gather turns each coroutine into a task, so both start before either ends. The results still come back in the order you passed them, not the order they finished."""

    async def main(log):
        return await asyncio.gather(fetch("slow", 0.03, log), fetch("fast", 0.01, log))

    log = []
    assert asyncio.run(main(log)) == ["SLOW", "FAST"]
    assert log == ["start slow", "start fast", "end fast", "end slow"]


def test_create_task_schedules_now_and_await_collects_later():
    """A task starts at the next hand-back, not at create_task itself. asyncio.sleep(0) is that hand-back. The await at the end only collects a result that may already exist."""

    async def main(log):
        task = asyncio.create_task(fetch("bg", 0.01, log))
        log.append("scheduled")
        await asyncio.sleep(0)
        log.append("after yield")
        result = await task
        return result

    log = []
    assert asyncio.run(main(log)) == "BG"
    assert log == ["scheduled", "start bg", "after yield", "end bg"]


def test_a_task_group_waits_for_every_task_before_the_block_ends():
    """Leaving the async with block is an await on all of its tasks. Nothing after the block runs until the slowest one is done."""

    async def main(log):
        async with asyncio.TaskGroup() as group:
            slow = group.create_task(fetch("slow", 0.02, log))
            fast = group.create_task(fetch("fast", 0.01, log))
        log.append("all done")
        return [slow.result(), fast.result()]

    log = []
    assert asyncio.run(main(log)) == ["SLOW", "FAST"]
    assert log[-2:] == ["end slow", "all done"]


def test_a_task_group_cancels_the_rest_when_one_fails():
    """One task raising cancels its siblings, so the one-second fetch never reaches its end. The errors arrive together in an ExceptionGroup, whose exceptions attribute lists them."""

    async def main(log):
        try:
            async with asyncio.TaskGroup() as group:
                group.create_task(boom())
                group.create_task(fetch("slow", 1.0, log))
        except ExceptionGroup as errors:
            log.append("caught")
            return log, errors.exceptions
        return log, ()

    log, exceptions = asyncio.run(main([]))
    assert log == ["start slow", "caught"]
    assert type(exceptions[0]) is ValueError


def test_timeout_cancels_what_is_inside_and_raises_timeout_error():
    """asyncio.timeout is an async with block with a deadline. When the deadline passes, the fetch inside is cancelled at its await and the block raises TimeoutError instead."""

    async def main(log):
        async with asyncio.timeout(0.01):
            await fetch("slow", 1.0, log)

    log = []
    with pytest.raises(TimeoutError):
        asyncio.run(main(log))
    assert log == ["start slow"]


def test_cancel_arrives_inside_the_task_as_cancelled_error():
    """task.cancel() asks; the CancelledError is delivered at the task's next await. The task may log or clean up, but it must re-raise, and then the awaiting side sees the same error."""

    async def main(log):
        task = asyncio.create_task(patient(log))
        await asyncio.sleep(0)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            log.append("cancelled outside")
        return task.cancelled()

    log = []
    assert asyncio.run(main(log)) is True
    assert log == ["cancelled inside", "cancelled outside"]


def test_time_sleep_freezes_every_task_but_asyncio_sleep_does_not():
    """gather starts blocking first. time.sleep is not an await, so the loop cannot switch and fetch cannot even start until it returns. polite awaits, so fetch runs during its pause."""

    async def with_blocking(log):
        await asyncio.gather(blocking(log), fetch("other", 0.01, log))

    async def with_polite(log):
        await asyncio.gather(polite(log), fetch("other", 0.01, log))

    frozen, shared = [], []
    asyncio.run(with_blocking(frozen))
    asyncio.run(with_polite(shared))
    assert frozen == ["start block", "end block", "start other", "end other"]
    assert shared == ["start polite", "start other", "end other", "end polite"]


def test_first_done_returns_the_quickest_and_cancels_the_rest():
    """Implement first_done above. 1. Make a list of tasks with asyncio.create_task(coro) for each coro in coroutines. 2. done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED); done and pending are sets of tasks. 3. For each task in pending, call task.cancel(). 4. Return done.pop().result()."""
    log = []
    assert asyncio.run(first_done(fetch("slow", 0.05, log), fetch("fast", 0.01, log))) == "FAST"
    assert "end fast" in log
    assert "end slow" not in log
