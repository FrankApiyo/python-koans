"""Properties and encapsulation.

Python has no private attributes. Every attribute of every object can be
read and written from anywhere. What it has instead is a convention: a name
that starts with one underscore, like _celsius, tells readers "internal, do
not touch from outside". Nothing enforces it.

A property is a method that is read like an attribute. Put @property above
a method that takes only self, and callers write t.celsius with no
parentheses. Add a setter and t.celsius = 30 runs a second method, which
can check the value before storing it.

    class Temperature:
        def __init__(self, celsius):
            self._celsius = celsius

        @property
        def celsius(self):
            return self._celsius

        @celsius.setter
        def celsius(self, value):
            self._celsius = value

    t = Temperature(20)
    t.celsius           # 20, the getter ran
    t.celsius = 30      # the setter ran

Callers cannot tell a property from a plain attribute. Start plain, and when
you later need validation or a computed value, switch. No caller changes.
"""

import pytest

from conftest import __


class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32


def test_an_underscore_is_a_convention_not_a_wall():
    """_celsius asks you not to touch it. Python still lets you. vars shows it is the only thing stored on the instance."""
    t = Temperature(20)
    assert t._celsius == 20
    assert vars(t) == {"_celsius": 20}


def test_a_property_reads_like_an_attribute():
    """celsius is given. @property makes t.celsius call the method for you, so t.celsius is already the number 20. Calling a number, as in 20(), is a TypeError."""
    t = Temperature(20)
    assert t.celsius == 20
    with pytest.raises(TypeError):
        t.celsius()


def test_a_property_without_a_setter_is_read_only():
    """Circle.radius has a getter and nothing else. Assigning to it raises AttributeError, and the stored value is untouched."""

    class Circle:
        def __init__(self, radius):
            self._radius = radius

        @property
        def radius(self):
            return self._radius

    c = Circle(1)
    with pytest.raises(AttributeError):
        c.radius = 2
    assert c.radius == 1


def test_a_computed_property_is_never_stale():
    """Implement Temperature.fahrenheit above. 1. Return self._celsius * 9 / 5 + 32. Nothing is stored: the value is worked out fresh on every read, so it always agrees with _celsius."""
    t = Temperature(100)
    assert t.fahrenheit == 212
    t._celsius = 0
    assert t.fahrenheit == 32
    assert vars(t) == {"_celsius": 0}


def test_a_setter_validates_before_storing():
    """Implement the Temperature.celsius setter above. 1. If value is below -273.15, raise ValueError. 2. Otherwise store value in self._celsius. The @celsius.setter line is already written; it makes t.celsius = x call this method with x as value."""
    t = Temperature(20)
    t.celsius = 25
    assert t.celsius == 25
    with pytest.raises(ValueError):
        t.celsius = -300
    assert t.celsius == 25


def test_the_setter_runs_inside_init_too():
    """self.celsius = celsius inside __init__ is an ordinary assignment through the property, so the setter checks the very first value. Temperature above skips the check by writing self._celsius directly."""

    class Checked:
        def __init__(self, celsius):
            self.celsius = celsius

        @property
        def celsius(self):
            return self._celsius

        @celsius.setter
        def celsius(self, value):
            if value < -273.15:
                raise ValueError("below absolute zero")
            self._celsius = value

    assert Checked(20).celsius == 20
    with pytest.raises(ValueError):
        Checked(-300)


def test_a_double_underscore_mangles_the_name():
    """A name that starts with two underscores and ends with at most one is renamed inside the class body: __secret becomes _Vault__secret. This keeps a subclass from clashing with it by accident."""

    class Vault:
        def __init__(self):
            self.__secret = 42

    assert vars(Vault()) == {"_Vault__secret": 42}


def test_mangling_is_not_privacy():
    """Outside the class body no renaming happens, so v.__secret is just a name that was never set, the same error as in chapter 01. Spell out the mangled name and the value is yours."""

    class Vault:
        def __init__(self):
            self.__secret = 42

    v = Vault()
    with pytest.raises(AttributeError):
        v.__secret
    assert v._Vault__secret == 42


def test_slots_forbid_new_attributes():
    """__slots__ names the only attributes an instance may have. The instance has no __dict__, the dict that vars showed in chapter 01, so p.y = 2 has nowhere to go and raises AttributeError. hasattr(obj, name) is True when obj.name would succeed."""

    class Point:
        __slots__ = ("x",)

        def __init__(self, x):
            self.x = x

    p = Point(1)
    assert p.x == 1
    with pytest.raises(AttributeError):
        p.y = 2
    assert hasattr(p, "__dict__") is False


def test_properties_let_you_change_your_mind():
    """report reads square.area and cannot tell which class it got. The first stores area, the second computes it. Switching from one to the other changes no caller."""

    class StoredSquare:
        def __init__(self, side):
            self.side = side
            self.area = side * side

    class ComputedSquare:
        def __init__(self, side):
            self.side = side

        @property
        def area(self):
            return self.side * self.side

    def report(square):
        return f"area is {square.area}"

    assert report(StoredSquare(3)) == "area is 9"
    assert report(ComputedSquare(3)) == "area is 9"
