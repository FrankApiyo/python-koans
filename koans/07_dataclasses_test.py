"""Dataclasses.

Writing __init__, __repr__ and __eq__ by hand for a class that is mostly
data is dull and easy to get wrong. The @dataclass decorator writes them
for you. It reads the annotated names in the class body, in order, and each
one becomes a field: a parameter of __init__, a part of repr, and a part
of ==.

    from dataclasses import dataclass

    @dataclass
    class Point:
        x: int
        y: int = 0

    Point(3)               # Point(x=3, y=0)
    Point(3) == Point(3)   # True

A field with a value after the = has a default. Fields without defaults
must come first, as parameters of a plain function must. A list or dict as
a default would be shared by every instance, the chapter 01 trap, so
dataclass refuses it; write field(default_factory=list) to get a fresh list
per instance. field(init=False) keeps a field out of __init__ entirely.

The decorator takes options. frozen=True makes instances read-only and
hashable. order=True adds <, <=, > and >=, comparing fields left to right
the way tuples do. If the class defines __post_init__, the generated
__init__ calls it as its last step, which is the place to compute one field
from the others. The dataclasses module also has asdict, which turns an
instance into a dict, and replace, which copies one with some fields changed.

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

from dataclasses import FrozenInstanceError, asdict, dataclass, field, replace
from typing import NamedTuple

import pytest

from conftest import __


@dataclass
class Point:
    x: int
    y: int = 0


@dataclass
class Name:
    first: str
    last: str
    full: str = field(init=False)

    def __post_init__(self):
        self.full = f"{self.first} {self.last}"


@dataclass
class Rect:
    w: int
    h: int
    area: int = field(init=False)

    def __post_init__(self):
        __()


def test_dataclass_writes_init_for_you():
    """Point has no __init__ in its body. @dataclass wrote one that takes x and y, in the order the annotations appear."""
    p = Point(3, 4)
    assert p.x == __
    assert p.y == __


def test_dataclass_writes_repr_for_you():
    """The generated repr names the class and every field with its value, in order. It looks like the call that would rebuild the object, as chapter 02 asked."""
    assert repr(Point(3, 4)) == __


def test_dataclass_writes_eq_for_you():
    """Chapter 01 said two instances are unequal by default. The generated __eq__ compares field by field, so the same data means equal objects."""
    assert (Point(3, 4) == Point(3, 4)) is __
    assert (Point(3, 4) == Point(4, 3)) is __


def test_a_field_with_a_value_has_a_default():
    """y: int = 0 makes y optional in __init__. Leave it out and you get 0. Pass it by position or by name to override."""
    assert Point(3).y == __
    assert Point(3, y=7).y == __


def test_a_required_field_cannot_follow_one_with_a_default():
    """The generated __init__ is a plain function, and a function may not put a required parameter after an optional one. dataclass raises TypeError while building the class, not when you call it."""
    with pytest.raises(__):

        @dataclass
        class Bad:
            x: int = 0
            y: int


def test_default_factory_makes_a_fresh_value_per_instance():
    """field(default_factory=list) calls list() for every new instance, so each one gets its own empty list and appending to one does not touch another."""

    @dataclass
    class Bag:
        items: list = field(default_factory=list)

    a = Bag()
    b = Bag()
    a.items.append(1)
    assert a.items == __
    assert b.items == __


def test_a_mutable_default_is_refused():
    """items: list = [] would hand every instance the same list, the chapter 01 trap. dataclass refuses it with ValueError while building the class and tells you to use default_factory."""
    with pytest.raises(__):

        @dataclass
        class Bad:
            items: list = []


def test_frozen_forbids_assignment_and_allows_hashing():
    """frozen=True makes assigning to a field raise FrozenInstanceError. Since the fields can never change, dataclass also writes __hash__ from them, so frozen instances can go in a set. Point is not frozen, so as chapter 02 warned, its __eq__ cost it its hash."""

    @dataclass(frozen=True)
    class Pixel:
        x: int
        y: int

    px = Pixel(1, 2)
    with pytest.raises(__):
        px.x = 5
    assert len({Pixel(1, 2), Pixel(1, 2), Pixel(2, 1)}) == __


def test_order_compares_fields_left_to_right():
    """order=True writes <, <=, > and >=. The first field decides; only a tie moves on to the second, as with tuples. Without order=True, < raises TypeError."""

    @dataclass(order=True)
    class Version:
        major: int
        minor: int

    assert (Version(1, 9) < Version(2, 0)) is __
    ordered = sorted([Version(2, 0), Version(1, 10), Version(1, 9)])
    assert ordered == __
    with pytest.raises(TypeError):
        Point(1) < Point(2)


def test_post_init_runs_after_the_generated_init():
    """Name is given. field(init=False) keeps full out of __init__, and the generated __init__ calls __post_init__ as its last step, which is where full is built from the other two fields."""
    n = Name("Ada", "Lovelace")
    assert n.full == __
    assert repr(n) == __


def test_post_init_computes_a_field_from_the_others():
    """Implement Rect.__post_init__ above. 1. area is declared with field(init=False), so the generated __init__ neither accepts it nor sets it. 2. By the time __post_init__ runs, self.w and self.h are already stored, so set self.area to self.w times self.h."""
    r = Rect(2, 3)
    assert r.area == 6
    assert repr(r) == "Rect(w=2, h=3, area=6)"
    assert Rect(2, 3) == Rect(2, 3)
    with pytest.raises(TypeError):
        Rect(2, 3, 6)


def test_asdict_turns_an_instance_into_a_dict():
    """asdict walks the fields and builds a plain dict with field names as keys. A field that is itself a dataclass becomes a nested dict, which is what json.dumps wants."""

    @dataclass
    class Segment:
        start: Point
        end: Point

    assert asdict(Point(3, 4)) == __
    segment = Segment(Point(0, 0), Point(1, 1))
    assert asdict(segment) == __


def test_replace_copies_with_some_fields_changed():
    """replace passes every field of the original to __init__, with the ones you name overridden, and returns the new instance. The original is untouched. This is how you change a frozen instance."""
    p = Point(3, 4)
    moved = replace(p, x=10)
    assert moved == __
    assert p.x == __
    assert (moved is p) is False


def test_a_namedtuple_is_the_tuple_shaped_cousin():
    """typing.NamedTuple reads annotations the same way but builds a tuple subclass: fields by name or by index, always frozen and hashable, and equal to a plain tuple with the same values. A dataclass never equals a tuple. Reach for NamedTuple when the data is a tuple in spirit; for anything with methods or changing state, use a dataclass."""

    class Pair(NamedTuple):
        x: int
        y: int = 0

    p = Pair(3, 4)
    assert p.x == 3
    assert p[1] == __
    assert (p == (3, 4)) is __
    assert (Point(3, 4) == (3, 4)) is False
    with pytest.raises(AttributeError):
        p.x = 5
