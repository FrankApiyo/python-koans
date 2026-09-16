"""Classmethods and staticmethods.

A plain method receives the instance as self. Two decorators change that.

@classmethod hands the method the class itself, called cls by convention,
whether you call it on the class or on an instance. Use it for alternate
constructors, which build an instance some other way than __init__, and
for reading or changing state shared by the whole class.

@staticmethod hands the method nothing at all. It is a plain function kept
in the class body because it belongs with the class. It sees no self or cls.

    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

        @classmethod
        def origin(cls):
            return cls(0, 0)

        @staticmethod
        def add(a, b):
            return a + b

    Point.origin()       # a Point at 0, 0
    Point.add(1, 2)      # 3

Inside a classmethod, cls(0, 0) calls whichever class it was handed. A
subclass, written class GridPoint(Point): and starting with everything
Point has, therefore gets a GridPoint back. Chapter 05 has the details.

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

import math

from conftest import __


class Point:
    count = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        Point.count += 1

    @classmethod
    def kind(cls):
        return cls.__name__

    @classmethod
    def origin(cls):
        return cls(0, 0)

    @classmethod
    def from_string(cls, text):
        # >>> answer
        x, y = text.split(",")
        return cls(int(x), int(y))
        # <<<

    @staticmethod
    def distance(a, b):
        # >>> answer
        return math.hypot(a.x - b.x, a.y - b.y)
        # <<<

    @classmethod
    def reset_count(cls):
        # >>> answer
        cls.count = 0
        # <<<


class GridPoint(Point):
    pass


def test_classmethod_receives_the_class():
    """kind is given. Called on Point with no arguments, cls is Point itself, so cls.__name__ is the name chapter 01 read off Dog."""
    assert Point.kind() == _a("Point")
    assert Point.__name__ == _a("Point")


def test_origin_is_an_alternate_constructor():
    """origin is given. cls(0, 0) is Point(0, 0) when called on Point. A classmethod that returns a new instance is a second way to build one."""
    o = Point.origin()
    assert (o.x, o.y) == _a((0, 0))
    assert type(o) is _a(Point)


def test_from_string_is_another_alternate_constructor():
    """Implement Point.from_string above. 1. Split text on the comma with text.split(","), which gives a list of two strings; unpack it into x and y. 2. Turn each into a number with int. 3. Return cls(x, y), not Point(x, y)."""
    p = Point.from_string("3,4")
    assert p.x == 3
    assert p.y == 4
    assert type(p) is Point


def test_cls_is_not_hardcoded():
    """GridPoint inherits from_string unchanged. Called on GridPoint, cls is GridPoint, so cls(x, y) builds a GridPoint. Had it said Point(x, y), a subclass could never use it."""
    g = GridPoint.from_string("1,2")
    assert type(g) is _a(GridPoint)
    assert g.kind() == _a("GridPoint")


def test_staticmethod_receives_nothing():
    """Implement Point.distance above. 1. a and b are both Points; there is no self or cls. 2. Return math.hypot(a.x - b.x, a.y - b.y). hypot takes two side lengths and returns the straight-line distance, the square root of their squares added."""
    assert Point.distance(Point(0, 0), Point(3, 4)) == 5.0
    assert Point.distance(Point(1, 1), Point(1, 1)) == 0.0


def test_both_work_on_instances_too():
    """Looking either kind up through an instance works. Python still passes the class to a classmethod and nothing to a staticmethod. Neither ever sees the instance."""
    p = Point(3, 4)
    assert p.kind() == _a("Point")
    assert p.distance(p, p.origin()) == _a(5.0)


def test_class_attribute_as_counter():
    """count = 0 in the class body is one shared number. __init__ does Point.count += 1, writing on the class, so every construction bumps the same count. It is reset by hand here because earlier koans built Points too."""
    Point.count = 0
    Point(1, 2)
    Point(3, 4)
    assert Point.count == _a(2)
    assert Point(5, 6).count == _a(3)


def test_classmethod_can_reset_shared_state():
    """Implement Point.reset_count above. 1. Assign 0 to cls.count. Assigning through cls writes the class attribute, the same place __init__ increments, and no instance is needed to do it."""
    Point(1, 2)
    Point(3, 4)
    Point.reset_count()
    assert Point.count == 0
    Point(5, 6)
    assert Point.count == 1


def test_when_to_use_which():
    """Ask what the code needs. This instance's own data: a method. The class, with no instance in hand: a classmethod. Neither, it only belongs near the class: a staticmethod."""
    move_this_point_one_step_right = "method"
    build_a_point_from_a_dict_of_x_and_y = _a("classmethod")
    say_whether_two_floats_are_within_a_tolerance = _a("staticmethod")
    assert [
        move_this_point_one_step_right,
        build_a_point_from_a_dict_of_x_and_y,
        say_whether_two_floats_are_within_a_tolerance,
    ] == ["method", "classmethod", "staticmethod"]
