"""Classes and instances.

A class is a blueprint. Calling it, as in Dog(), builds one object from that
blueprint and hands it back. That object is an instance. Each call makes a
fresh one.

    class Dog:
        def __init__(self, name):
            self.name = name

        def speak(self):
            return f"{self.name} says woof"

    rex = Dog("Rex")
    rex.speak()          # 'Rex says woof'

Python runs __init__ on every new instance, passing the instance itself as
the first argument. Inside the class that argument is called self by
convention. Anything you attach to self, like self.name, becomes an
attribute of that one instance. A method is just a function defined in the
class body; rex.speak() is shorthand for Dog.speak(rex).

A variable assigned in the class body, outside any method, is a class
attribute. Every instance can read it, and it lives in one place.
"""

import pytest

from conftest import __


class Dog:
    species = "Canis familiaris"
    born = []

    def __init__(self, name):
        self.name = name
        Dog.born.append(name)

    def speak(self):
        return f"{self.name} says woof"

    def me(self):
        return self


def test_calling_a_class_makes_an_instance():
    """The class is Dog. The thing Dog("Rex") returns is an instance of it."""
    rex = Dog("Rex")
    assert type(rex) is _a(Dog)
    assert isinstance(rex, Dog) is _a(True)


def test_two_calls_make_two_different_objects():
    """Even with the same arguments, each call builds a new object. is compares identity."""
    a = Dog("Rex")
    b = Dog("Rex")
    assert (a is b) is _a(False)
    assert (a is a) is _a(True)


def test_equality_is_identity_until_you_say_otherwise():
    """Two instances with the same data are not equal by default. Chapter 02 changes that."""
    assert (Dog("Rex") == Dog("Rex")) is _a(False)


def test_init_runs_when_you_call_the_class():
    """You never call __init__ yourself. Dog(...) calls it for you, once per instance."""
    Dog.born.clear()
    Dog("Rex")
    Dog("Fido")
    assert Dog.born == _a(["Rex", "Fido"])


def test_self_is_the_instance_the_method_was_called_on():
    """rex.me() is Dog.me(rex). Python fills in self with rex."""
    rex = Dog("Rex")
    assert (rex.me() is rex) is _a(True)
    assert (Dog.me(rex) is rex) is _a(True)


def test_you_can_name_self_anything_but_do_not():
    """The first parameter receives the instance whatever you call it. self is a convention every reader expects."""

    class Cat:
        def __init__(this, name):
            this.name = name

        def speak(this):
            return f"{this.name} says meow"

    assert Cat("Tom").speak() == _a("Tom says meow")


def test_attributes_are_set_on_self():
    """self.name = name inside __init__ stores name on this instance. Read it back with a dot."""
    rex = Dog("Rex")
    assert rex.name == _a("Rex")
    assert rex.speak() == _a("Rex says woof")


def test_attributes_can_be_added_after_construction():
    """An instance is a bag you can keep putting things in. vars shows what is in the bag."""
    rex = Dog("Rex")
    rex.tricks = ["sit"]
    assert vars(rex) == _a({"name": "Rex", "tricks": ["sit"]})


def test_missing_attribute_raises_attribute_error():
    """Reading a name that was never set on this instance or its class is an error, not None."""
    rex = Dog("Rex")
    with pytest.raises(_a(AttributeError)):
        rex.age


def test_class_attributes_are_shared():
    """species was assigned in the class body, not on self. Every Dog reads the same one."""
    rex = Dog("Rex")
    fido = Dog("Fido")
    assert rex.species == _a("Canis familiaris")
    assert (rex.species is fido.species) is _a(True)


def test_instance_attributes_shadow_class_attributes():
    """Assigning through an instance creates an attribute on that instance only. The class and other instances are untouched."""
    rex = Dog("Rex")
    fido = Dog("Fido")
    rex.species = "wolf"
    assert fido.species == _a("Canis familiaris")
    assert Dog.species == _a("Canis familiaris")


def test_a_mutable_class_attribute_is_a_trap():
    """Dog.born is one list shared by all. Appending through any instance changes it for every instance. Keep per-instance state on self."""
    Dog.born.clear()
    rex = Dog("Rex")
    fido = Dog("Fido")
    rex.born.append("Spot")
    assert fido.born == _a(["Rex", "Fido", "Spot"])


def test_everything_is_an_object():
    """Numbers, functions, and classes themselves are objects. The class of a class is type."""
    assert isinstance(3, object) is _a(True)
    assert type(Dog) is _a(type)
    assert Dog.__name__ == _a("Dog")
