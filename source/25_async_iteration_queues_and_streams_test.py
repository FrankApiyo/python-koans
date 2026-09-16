"""Async iteration, asyncio queues, and streams.

Chapter 08 taught that for calls iter() once and next() until StopIteration.
The async versions are the same shape with an await in each step. async for
calls __aiter__ once, then awaits __anext__ until it raises
StopAsyncIteration. A function that is async def and contains yield is an
async generator: each yield hands out one value, and the body may await
between yields, so a slow source can be looped over without blocking the
rest of the program. A plain for cannot drive one; that is a TypeError.

    async def numbers():
        yield 1
        yield 2

    [x async for x in numbers()]      # [1, 2], inside a coroutine

asyncio.Queue is chapter 22's queue.Queue for tasks instead of threads.
await q.put(item) adds, await q.get() waits until something is there. Each
q.task_done() marks one got item as finished, and await q.join() waits
until every put item has been marked, which lets the producer know the
work is done without a sentinel.

A stream is a socket read through a reader and written through a writer.
start_server takes a handler(reader, writer) coroutine and an address; port
0 lets the OS pick a free port, and server.sockets[0].getsockname() reveals
it. open_connection returns the client's pair. write() only buffers, await
drain() waits until the buffer has emptied enough to keep writing. readline() reads through a newline,
readexactly(n) reads n bytes or raises IncompleteReadError, read() with no
size reads to the end. The end is empty bytes, b"", caused by the other
side's write_eof() or close(). Always close() a writer, then await
wait_closed().

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

import asyncio
import contextlib
import signal

import pytest

from conftest import __


class Countdown:
    def __init__(self, start):
        self.current = start

    def __aiter__(self):
        return self

    async def __anext__(self):
        # >>> answer
        if self.current <= 0:
            raise StopAsyncIteration
        value = self.current
        self.current -= 1
        return value
        # <<<


async def ticker(n, delay):
    for i in range(n):
        # >>> answer
        await asyncio.sleep(delay)
        # <<<
        yield i


@contextlib.contextmanager
def watchdog(seconds):
    """A handler that never awaits never lets the loop run, so asyncio.timeout cannot fire. An alarm signal can."""
    if not hasattr(signal, "SIGALRM"):
        yield
        return

    def bark(signum, frame):
        raise TimeoutError("the handler never handed control back to the event loop")

    previous = signal.signal(signal.SIGALRM, bark)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


async def echo_handler(reader, writer):
    # >>> answer
    while True:
        line = await reader.readline()
        if not line:
            break
        writer.write(line)
        await writer.drain()
    writer.close()
    await writer.wait_closed()
    # <<<


async def numbers():
    yield 1
    yield 2


async def hello_handler(reader, writer):
    writer.write(b"hello\n")
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def abc_handler(reader, writer):
    writer.write(b"abcdef")
    await writer.drain()
    writer.close()
    await writer.wait_closed()


def port_of(server):
    return server.sockets[0].getsockname()[1]


def test_async_for_drives_an_async_generator():
    """async for is for with an await in each step. A yield inside async def makes an async generator, which has __anext__ instead of __next__."""

    async def main():
        seen = []
        async for n in numbers():
            seen.append(n)
        return seen

    assert asyncio.run(main()) == _a([1, 2])
    assert hasattr(numbers(), "__anext__") is _a(True)


def test_a_plain_for_cannot_drive_it():
    """An async generator has no __iter__ and no __next__. Only async for, or the anext() builtin under an await, can ask it for values."""
    with pytest.raises(_a(TypeError)):
        for n in numbers():
            pass


def test_anext_is_awaited_and_ends_with_its_own_exception():
    """anext(it) returns an awaitable for the next value, the way next(it) returns the value. The end is StopAsyncIteration, a different class from StopIteration."""

    async def main():
        it = numbers()
        first = await anext(it)
        second = await anext(it)
        try:
            await anext(it)
        except StopAsyncIteration:
            return first, second, "stopped"

    assert asyncio.run(main()) == _a((1, 2, "stopped"))


def test_anext_counts_down_like_chapter_08():
    """Implement Countdown.__anext__ above. 1. If self.current is 0 or less, raise StopAsyncIteration. 2. Otherwise remember self.current, subtract one from it, and return the remembered value. It is chapter 08's __next__ with async def in front and a different stop exception."""

    async def main():
        return [n async for n in Countdown(3)]

    assert asyncio.run(main()) == [3, 2, 1]


def test_an_async_generator_may_await_between_yields():
    """Implement ticker above. 1. Inside the loop, before the yield that is already written, await asyncio.sleep(delay). An await between yields is what a plain generator can never do, and it is the whole reason async for exists."""

    async def main():
        return [i async for i in ticker(3, 0)]

    assert asyncio.run(main()) == [0, 1, 2]
    assert asyncio.run(main()) == [0, 1, 2]


def test_async_comprehensions_collect_without_a_loop():
    """A comprehension with async for inside it builds a list, set, or dict from an async source. It is only legal inside a coroutine."""

    async def main():
        doubled = [n * 2 async for n in numbers()]
        keyed = {n: str(n) async for n in numbers()}
        return doubled, keyed

    doubled, keyed = asyncio.run(main())
    assert doubled == _a([2, 4])
    assert keyed == _a({1: "1", 2: "2"})


def test_a_queue_hands_items_from_one_task_to_another():
    """The producer puts, the consumer gets, and a None at the end tells the consumer to stop. This is chapter 22's pattern with await in front of put and get."""

    async def produce(q):
        for n in [1, 2, 3]:
            await q.put(n)
        await q.put(None)

    async def consume(q, seen):
        while True:
            item = await q.get()
            if item is None:
                return
            seen.append(item)

    async def main():
        q = asyncio.Queue()
        seen = []
        async with asyncio.TaskGroup() as tg:
            tg.create_task(produce(q))
            tg.create_task(consume(q, seen))
        return seen

    assert asyncio.run(main()) == _a([1, 2, 3])


def test_get_waits_until_something_is_put():
    """await q.get() on an empty queue parks the consumer until a put arrives. The log shows the consumer waiting before the put and receiving after it."""

    async def main():
        q = asyncio.Queue()
        log = []

        async def consume():
            log.append("waiting")
            item = await q.get()
            log.append(f"got {item}")

        task = asyncio.create_task(consume())
        await asyncio.sleep(0)
        log.append("put")
        await q.put(1)
        await task
        return log

    assert asyncio.run(main()) == _a(["waiting", "put", "got 1"])


def test_task_done_and_join_replace_the_sentinel():
    """q.join() waits until every put item has been matched by a task_done(). The worker never needs to know how many items there are, and the producer cancels it once join returns."""

    async def work(q, seen):
        while True:
            item = await q.get()
            seen.append(item)
            q.task_done()

    async def main():
        q = asyncio.Queue()
        seen = []
        worker = asyncio.create_task(work(q, seen))
        for n in [1, 2, 3]:
            await q.put(n)
        await q.join()
        worker.cancel()
        return seen, q.qsize()

    assert asyncio.run(main()) == _a(([1, 2, 3], 0))


def test_join_waits_for_task_done_not_for_get():
    """Getting an item does not count as finishing it. Until task_done() is called join keeps waiting, which is why a forgotten task_done() hangs a program."""

    async def main():
        q = asyncio.Queue()
        await q.put("job")
        await q.get()
        outcome = "finished"
        try:
            await asyncio.wait_for(q.join(), 0.05)
        except TimeoutError:
            outcome = "still waiting"
        q.task_done()
        await q.join()
        return outcome

    assert asyncio.run(main()) == _a("still waiting")


def test_a_server_is_a_handler_and_an_address():
    """start_server calls the handler once per connection. Port 0 lets the OS choose, getsockname reveals the choice, and the client reads the handler's line then b"" once the handler closes."""

    async def main():
        server = await asyncio.start_server(hello_handler, "127.0.0.1", 0)
        async with server, asyncio.timeout(1):
            reader, writer = await asyncio.open_connection("127.0.0.1", port_of(server))
            line = await reader.readline()
            rest = await reader.read()
            writer.close()
            await writer.wait_closed()
        return line, rest

    line, rest = asyncio.run(main())
    assert line == _a(b"hello\n")
    assert rest == _a(b"")


def test_an_echo_handler_reads_lines_until_eof():
    """Implement echo_handler above. 1. Loop forever: line = await reader.readline(). 2. If line is empty bytes the client is done, so break. 3. Otherwise writer.write(line) and await writer.drain(). 4. After the loop, writer.close() and await writer.wait_closed(). The client's write_eof() is what produces the empty line."""

    async def main():
        server = await asyncio.start_server(echo_handler, "127.0.0.1", 0)
        async with server, asyncio.timeout(1):
            reader, writer = await asyncio.open_connection("127.0.0.1", port_of(server))
            replies = []
            for line in [b"one\n", b"two\n"]:
                writer.write(line)
                await writer.drain()
                replies.append(await reader.readline())
            writer.write_eof()
            tail = await reader.read()
            writer.close()
            await writer.wait_closed()
        return replies, tail

    with watchdog(2):
        assert asyncio.run(main()) == ([b"one\n", b"two\n"], b"")


def test_readexactly_takes_a_fixed_count_or_complains():
    """readexactly(n) waits for n bytes. If the other side closes first it raises IncompleteReadError, and the bytes that did arrive are on the error's partial attribute."""

    async def main():
        server = await asyncio.start_server(abc_handler, "127.0.0.1", 0)
        async with server, asyncio.timeout(1):
            reader, writer = await asyncio.open_connection("127.0.0.1", port_of(server))
            head = await reader.readexactly(3)
            partial = b""
            try:
                await reader.readexactly(10)
            except asyncio.IncompleteReadError as error:
                partial = error.partial
            writer.close()
            await writer.wait_closed()
        return head, partial

    head, partial = asyncio.run(main())
    assert head == _a(b"abc")
    assert partial == _a(b"def")
