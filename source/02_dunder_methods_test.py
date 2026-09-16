"""Dunder methods.

Python's operators and builtins are not magic. Each one turns into a call to
a method with double underscores on both sides, a "dunder" method, and you
can define them on your own classes.

    len(x)      calls  x.__len__()
    x == y      calls  x.__eq__(y)
    x + y       calls  x.__add__(y)
    x < y       calls  x.__lt__(y)
    x[i]        calls  x.__getitem__(i)
    repr(x)     calls  x.__repr__()
    str(x)      calls  x.__str__(), falling back to __repr__

repr is for developers: it should look like the code that would rebuild the
object. str is for people. If you write only __repr__, both use it.

Defining __eq__ silently removes the default __hash__, because equal objects
must hash the same and Python cannot guess how. Objects without a hash cannot
go in a set or be dict keys. Define __hash__ over the same fields as __eq__.

A method that cannot handle the other operand should return NotImplemented,
the value, so Python can try the other side or raise a clean TypeError.

Money below is built up one dunder at a time. Every koan says which.

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

import functools

import pytest

from conftest import __


class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        # >>> answer
        return f"Money({self.amount}, {self.currency!r})"
        # <<<

    def __str__(self):
        # >>> answer
        return f"{self.amount} {self.currency}"
        # <<<

    def __eq__(self, other):
        # >>> answer
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency
        # <<<

    def __hash__(self):
        # >>> answer
        return hash((self.amount, self.currency))
        # <<<

    def __add__(self, other):
        # >>> answer
        if self.currency != other.currency:
            raise ValueError("currencies differ")
        return Money(self.amount + other.amount, self.currency)
        # <<<

    def __lt__(self, other):
        # >>> answer
        return self.amount < other.amount
        # <<<


class Plain:
    def __init__(self, x):
        self.x = x


class Playlist:
    def __init__(self, *songs):
        self._songs = list(songs)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        return self._songs[index]


class AlwaysTrue:
    def __len__(self):
        return 0

    def __bool__(self):
        return True


def test_the_default_repr_says_almost_nothing():
    """Without __repr__ you get the class name and a memory address. Useless in a test failure."""
    assert repr(Plain(1)).startswith(_a("<"))
    assert "Plain object at" in repr(Plain(1))


def test_repr_is_for_developers():
    """Implement Money.__repr__ above. 1. Return an f-string that looks like the constructor call: Money(1, 'KES'). 2. Use {self.currency!r} so the string gets its quotes."""
    assert repr(Money(1, "KES")) == "Money(1, 'KES')"


def test_str_is_for_people():
    """Implement Money.__str__ above. 1. Return the amount, a space, and the currency, as in 1 KES."""
    assert str(Money(1, "KES")) == "1 KES"
    assert f"{Money(1, 'KES')}" == "1 KES"


def test_str_falls_back_to_repr():
    """A class with only __repr__ uses it for str and print too."""

    class Tagged:
        def __repr__(self):
            return "Tagged()"

    assert str(Tagged()) == _a("Tagged()")


def test_equality_is_identity_by_default():
    """Two Plain objects with the same x are still different objects, so == is False."""
    assert (Plain(1) == Plain(1)) is _a(False)


def test_eq_defines_equality():
    """Implement Money.__eq__ above. 1. If other is not a Money, return NotImplemented. 2. Otherwise return whether both amount and currency match."""
    assert Money(1, "KES") == Money(1, "KES")
    assert (Money(1, "KES") == Money(2, "KES")) is False
    assert (Money(1, "KES") == Money(1, "USD")) is False
    assert (Money(1, "KES") == 1) is False


def test_defining_eq_deletes_hash():
    """A class with __eq__ and no __hash__ cannot be hashed, so it cannot go in a set. Python refuses to guess."""

    class Coin:
        def __init__(self, value):
            self.value = value

        def __eq__(self, other):
            return self.value == other.value

    with pytest.raises(_a(TypeError)):
        {Coin(1)}


def test_hash_must_agree_with_eq():
    """Implement Money.__hash__ above. 1. Return hash of the tuple (self.amount, self.currency), the same fields __eq__ compares. Equal objects now hash equal, so a set can spot duplicates."""
    assert hash(Money(1, "KES")) == hash(Money(1, "KES"))
    assert len({Money(1, "KES"), Money(1, "KES"), Money(2, "KES")}) == 2


def test_add_makes_plus_work():
    """Implement Money.__add__ above. 1. If the currencies differ, raise ValueError. 2. Otherwise return a new Money with the amounts summed and the same currency. Do not change self."""
    total = Money(1, "KES") + Money(2, "KES")
    assert total == Money(3, "KES")
    with pytest.raises(ValueError):
        Money(1, "KES") + Money(1, "USD")


def test_lt_makes_sorted_work():
    """Implement Money.__lt__ above. 1. Return whether self.amount is less than other.amount. sorted, min and max only need this one comparison."""
    monies = [Money(3, "KES"), Money(1, "KES"), Money(2, "KES")]
    assert sorted(monies) == [Money(1, "KES"), Money(2, "KES"), Money(3, "KES")]
    assert min(monies) == Money(1, "KES")


def test_total_ordering_fills_in_the_rest():
    """Given __eq__ and one of the four comparisons, functools.total_ordering derives the other three."""

    @functools.total_ordering
    class Version:
        def __init__(self, n):
            self.n = n

        def __eq__(self, other):
            return self.n == other.n

        def __lt__(self, other):
            return self.n < other.n

    assert (Version(2) >= Version(1)) is _a(True)
    assert (Version(1) > Version(2)) is _a(False)


def test_len_and_getitem():
    """__len__ answers len. __getitem__ answers square brackets, negative indexes included, because it hands the index to a list."""
    p = Playlist("a", "b", "c")
    assert len(p) == _a(3)
    assert p[0] == _a("a")
    assert p[-1] == _a("c")


def test_getitem_gives_you_for_and_in_for_free():
    """With only __getitem__, Python iterates by asking for 0, 1, 2 until IndexError. in and list use that."""
    p = Playlist("a", "b", "c")
    assert list(p) == _a(["a", "b", "c"])
    assert ("b" in p) is _a(True)


def test_bool_defaults_to_len():
    """Truth testing calls __bool__ if present, else __len__ and asks if it is non-zero. AlwaysTrue has __bool__ so its empty length does not matter."""
    assert bool(Playlist()) is _a(False)
    assert bool(Playlist("a")) is _a(True)
    assert bool(AlwaysTrue()) is _a(True)
