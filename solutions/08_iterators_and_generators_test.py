"""Iterators and generators.

A for loop does two things behind the scenes. First it calls iter() on the
thing you gave it and gets back an iterator. Then it calls next() on that
iterator again and again, and stops when next() raises StopIteration.

    it = iter([10, 20])
    next(it)             # 10
    next(it)             # 20
    next(it)             # raises StopIteration

An iterable is anything with __iter__, which must return an iterator. An
iterator is anything with __next__, which returns the next value or raises
StopIteration when none are left, plus an __iter__ that returns itself so
for accepts it too. A list is iterable but not an iterator: iter(a_list)
builds a fresh iterator each time, so a list can be looped over twice,
while an iterator is used up after one pass.

Writing __next__ by hand means keeping your position in an attribute. A
generator function does that bookkeeping for you. Any function with yield
in its body returns a generator when called, and the body does not run
until next() asks. Each yield hands out one value and pauses; the next
call resumes just after the yield; running off the end is the stop.

    def two():
        yield 1
        yield 2

    list(two())          # [1, 2]

A generator is an iterator. A method is a function, so a class becomes
iterable by writing __iter__ with a yield in it. Every structure later in
this course is made iterable that way.

Picture: lessons/svg/08_iterator_protocol.svg. Every chapter is also on lessons/index.html.
"""

from itertools import islice

import pytest

from conftest import __


class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


def countdown(n):
    while n > 0:
        yield n
        n -= 1


class Shelf:
    def __init__(self, *books):
        self._books = list(books)

    def __iter__(self):
        for book in self._books:
            yield book


def test_for_is_iter_then_next_until_it_stops():
    """iter() asks a list for an iterator. next() asks the iterator for one value at a time, in order."""
    it = iter(["a", "b", "c"])
    assert next(it) == "a"
    assert next(it) == "b"


def test_next_raises_stop_iteration_when_nothing_is_left():
    """The end is signalled by an exception, not by None. for catches it silently. next(it, default) returns default instead of raising."""
    it = iter([1])
    next(it)
    with pytest.raises(StopIteration):
        next(it)
    assert next(it, "done") == "done"


def test_a_list_is_iterable_but_not_an_iterator():
    """A list has __iter__ but no __next__. iter(a_list) builds an iterator that has both, and its __iter__ returns itself, so for can accept either one."""
    xs = [1, 2]
    it = iter(xs)
    assert hasattr(it, "__next__")
    assert hasattr(xs, "__next__") is False
    assert (iter(it) is it) is True


def test_iter_returns_self_so_countdown_is_its_own_iterator():
    """Implement Countdown.__iter__ above. 1. Return self. Countdown keeps its own position in self.current, so the object is both the iterable and the iterator, exactly like the list iterator in the last koan."""
    c = Countdown(3)
    assert iter(c) is c


def test_next_counts_down_and_stops_at_zero():
    """Implement Countdown.__next__ above. 1. If self.current is 0 or less, raise StopIteration. 2. Otherwise remember self.current in a local variable, subtract one from self.current, and return the remembered value."""
    c = Countdown(3)
    assert next(c) == 3
    assert next(c) == 2
    assert next(c) == 1
    with pytest.raises(StopIteration):
        next(c)
    assert list(Countdown(3)) == [3, 2, 1]


def test_an_iterator_is_used_up_after_one_pass():
    """Countdown keeps its position in self.current and never resets it. Once it has raised StopIteration every later next raises it too, so a second loop sees nothing. A list survives a second loop because iter() builds a fresh iterator each time."""
    c = Countdown(2)
    assert list(c) == [2, 1]
    assert list(c) == []


def test_yield_turns_a_function_into_a_generator():
    """Implement countdown above. 1. While n is greater than 0: yield n, then subtract one from n. No class, no self.current, no StopIteration: the local variable n is the position, and running off the end of the function is the stop."""
    gen = countdown(3)
    assert hasattr(gen, "__next__")
    assert next(gen) == 3
    assert list(gen) == [2, 1]
    assert list(countdown(3)) == [3, 2, 1]
    assert list(countdown(0)) == []


def test_a_generator_runs_only_when_asked():
    """Calling a generator function runs none of its body. Each next runs just far enough to reach the next yield. seen records every step the body has taken so far."""
    seen = []

    def numbers():
        for n in [1, 2, 3]:
            seen.append(n)
            yield n

    gen = numbers()
    assert seen == []
    next(gen)
    next(gen)
    assert seen == [1, 2]


def test_iter_written_with_yield_makes_any_class_iterable():
    """Implement Shelf.__iter__ above. 1. For each book in self._books, yield it. A method is a function, so a yield inside __iter__ makes it return a fresh generator on every call, and that generator is the iterator for wants. Unlike Countdown a Shelf survives a second loop, because each loop gets a new generator. Every structure in later chapters is made iterable this way."""
    shelf = Shelf("Dune", "Emma")
    assert list(shelf) == ["Dune", "Emma"]
    assert [book.lower() for book in shelf] == ["dune", "emma"]
    assert list(shelf) == ["Dune", "Emma"]


def test_yield_from_hands_out_everything_from_another_iterable():
    """yield from xs is a shortcut for: for x in xs, yield x. It accepts any iterable, whether a list, a string, or another generator."""

    def chain(first, second):
        yield from first
        yield from second

    assert list(chain([1, 2], "ab")) == [1, 2, "a", "b"]
    assert list(chain(countdown(2), countdown(1))) == [2, 1, 1]


def test_an_infinite_generator_needs_islice():
    """naturals never stops, so list(naturals()) would never finish. itertools.islice(it, stop) takes the first stop values and then stops asking; islice(it, start, stop) skips start values first. Laziness is what makes an endless generator usable."""

    def naturals():
        n = 1
        while True:
            yield n
            n += 1

    assert list(islice(naturals(), 3)) == [1, 2, 3]
    assert list(islice(naturals(), 3, 6)) == [4, 5, 6]
