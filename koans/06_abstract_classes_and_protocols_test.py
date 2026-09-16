"""Abstract classes and protocols.

Sometimes a base class exists only to say what its subclasses must
provide. An abstract base class, or ABC, lists methods that subclasses
must override. Mark the class with ABC and each such method with
@abstractmethod, both from the abc module. Python refuses to build an
instance of any class that still has an abstract method waiting, and
raises TypeError instead. The three dots below are Ellipsis, a value that
does nothing, used here as a placeholder body.

    from abc import ABC, abstractmethod

    class Shape(ABC):
        @abstractmethod
        def area(self):
            ...

    Shape()                      # TypeError
    class Square(Shape):
        def area(self):
            return 4
    Square().area()              # 4

The other way needs no base class at all. Duck typing means a function
uses whatever object it is given, as long as that object has the methods
the function calls: if it quacks, it is a duck. hasattr(obj, "quack") asks
before calling. typing.Protocol writes the duck down as a class listing
the methods. Annotations like thing: Quacker or -> str are notes; Python
does not check them when the code runs. Add @runtime_checkable and
isinstance can check the duck. collections.abc holds ready-made ones such
as Sized (has __len__) and Iterable (has __iter__).

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

import math
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence, Sized
from typing import Protocol, runtime_checkable

import pytest

from conftest import __


class Shape(ABC):
    @abstractmethod
    def area(self):
        ...

    def describe(self):
        return f"{type(self).__name__} with area {self.area()}"


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        __()


class Duck:
    def quack(self):
        return "Quack"


class Robot:
    def quack(self):
        return "beep"


def make_noise(thing):
    return thing.quack()


class Quacker(Protocol):
    def quack(self) -> str: ...


class Bag:
    def __init__(self, *items):
        self._items = list(items)

    def __len__(self):
        return len(self._items)


class Deck(Sequence):
    def __init__(self, *cards):
        self._cards = list(cards)

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, index):
        __()


def test_an_abc_cannot_be_instantiated():
    """Shape.area is abstract, so Shape() is refused. The class exists to be inherited from, not built."""
    with pytest.raises(__):
        Shape()


def test_a_subclass_that_forgets_is_still_abstract():
    """Blob inherits the abstract area and never overrides it. Python keeps the names still waiting in __abstractmethods__, and while that is not empty the class cannot be built."""

    class Blob(Shape):
        pass

    with pytest.raises(TypeError):
        Blob()
    assert Blob.__abstractmethods__ == __


def test_a_subclass_that_overrides_can_be_built():
    """Square overrides area, so nothing is left waiting. It also inherits describe, which calls the area Square provides."""
    assert Square(3).area() == __
    assert Square(3).describe() == __


def test_implement_the_abstract_method():
    """Implement Circle.area above. 1. Return math.pi times the radius squared, written math.pi * self.radius ** 2. With area overridden Circle has no abstract methods left and can be built."""
    assert Circle(1).area() == math.pi
    assert Circle(2).area() == math.pi * 4
    assert Circle.__abstractmethods__ == set()
    assert isinstance(Circle(1), Shape) is True


def test_abstract_methods_can_have_a_body_you_call_with_super():
    """@abstractmethod only marks the method. Its body stays, and a subclass that overrides it may run the original with super(), as chapter 05 did with __init__."""

    class Greeter(ABC):
        @abstractmethod
        def greet(self):
            return "hello"

    class Loud(Greeter):
        def greet(self):
            return super().greet().upper() + "!"

    assert Loud().greet() == __


def test_duck_typing_needs_no_base_class():
    """make_noise calls .quack() and nothing else. Duck and Robot share no base class, but both have quack, so both work."""
    assert make_noise(Duck()) == __
    assert make_noise(Robot()) == __
    assert issubclass(Robot, Duck) is False


def test_hasattr_checks_the_duck():
    """Calling quack on something without it raises AttributeError. hasattr(obj, name) answers True or False so you can ask before you call."""
    assert hasattr(Duck(), "quack") is __
    assert hasattr(3, "quack") is __
    with pytest.raises(AttributeError):
        make_noise(3)


def test_a_protocol_names_the_duck():
    """Quacker lists the one method a duck needs. A function annotated with it accepts anything that has quack. Python ignores the annotation, so nothing has to inherit from Quacker, and without runtime_checkable isinstance refuses to check it."""

    def loud(thing: Quacker) -> str:
        return thing.quack().upper()

    assert loud(Robot()) == __
    assert loud(Duck()) == "QUACK"
    with pytest.raises(__):
        isinstance(Robot(), Quacker)


def test_runtime_checkable_lets_isinstance_check():
    """@runtime_checkable makes isinstance look for the listed method names on the object. It checks that they exist, not what they return."""

    @runtime_checkable
    class CheckedQuacker(Protocol):
        def quack(self) -> str: ...

    assert isinstance(Robot(), CheckedQuacker) is __
    assert isinstance(3, CheckedQuacker) is __
    assert issubclass(Duck, CheckedQuacker) is True


def test_collections_abc_has_ready_made_ducks():
    """Sized means has __len__ and Iterable means has __iter__. Bag never inherits from Sized, yet isinstance says it is one. It has no __iter__, so it is not Iterable."""
    assert isinstance(Bag("a"), Sized) is __
    assert isinstance(Bag("a"), Iterable) is __
    assert isinstance("abc", Iterable) is True


def test_inheriting_from_sequence_fills_in_methods():
    """Implement Deck.__getitem__ above. 1. Return self._cards[index], handing the index to the list as Playlist did in chapter 02. Sequence declares __getitem__ and __len__ abstract and writes __iter__, __contains__, __reversed__, index and count on top of them, so once both exist the rest come free."""
    assert Sequence.__abstractmethods__ == {"__getitem__", "__len__"}
    deck = Deck("a", "k", "q", "k")
    assert deck[2] == "q"
    assert deck[-1] == "k"
    assert deck.index("k") == 1
    assert deck.count("k") == 2
    assert ("q" in deck) is True
    assert list(reversed(deck)) == ["k", "q", "k", "a"]
    assert isinstance(deck, Iterable) is True
