"""Inheritance and the MRO.

class Dog(Animal) says a Dog is an Animal: every method of Animal works on
a Dog with no extra code. Define a method of the same name in Dog and Dog's
version wins. That is overriding.

    class Animal:
        def __init__(self, name):
            self.name = name

        def speak(self):
            return "..."

    class Dog(Animal):
        def __init__(self, name, breed):
            super().__init__(name)
            self.breed = breed

        def speak(self):
            return "woof"

Reading dog.speak, Python looks in Dog, then Animal, then object, and stops
at the first class that has it. That ordered list is the method resolution
order, the MRO, and Dog.__mro__ holds it as a tuple. With several parents,
class C(A, B), the MRO goes left to right, lists each class exactly once,
and always puts a class before its own parents.

super() means "the next class after this one in the MRO of the object being
worked on". With one parent that is the parent, so super().__init__(name)
in Dog runs Animal's __init__. With several parents it can be a sibling
instead; the last koans show that. isinstance and issubclass walk the MRO.

Picture: lessons/svg/05_mro_diamond.svg. Every chapter is also on lessons/index.html.
"""

import json

import pytest

from conftest import __


class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

    def eat(self, food):
        return f"{self.name} eats {food}"


class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def speak(self):
        return "woof"


class Cat(Animal):
    def __init__(self, name, indoor):
        # >>> answer
        super().__init__(name)
        self.indoor = indoor
        # <<<

    def speak(self):
        # >>> answer
        return "meow"
        # <<<


class JsonMixin:
    def to_json(self):
        # >>> answer
        return json.dumps(vars(self))
        # <<<


class Bird(JsonMixin, Animal):
    pass


def test_a_subclass_inherits_methods():
    """Dog never defines eat. Lookup misses in Dog, finds it in Animal, and it is the very same function."""
    dog = Dog("Rex", "lab")
    assert dog.eat("bones") == _a("Rex eats bones")
    assert (Dog.eat is Animal.eat) is _a(True)


def test_a_subclass_overrides():
    """Dog defines its own speak, so lookup stops at Dog and never reaches Animal's. Animal itself is unchanged."""
    assert Animal("Generic").speak() == _a("...")
    assert Dog("Rex", "lab").speak() == _a("woof")


def test_super_init_runs_the_parent_init():
    """Dog.__init__ is given. super().__init__(name) runs Animal.__init__ on the same instance, so name is set before breed. Skip it and the parent's attributes never appear."""
    dog = Dog("Rex", "lab")
    assert vars(dog) == _a({"name": "Rex", "breed": "lab"})

    class Forgetful(Animal):
        def __init__(self, name, breed):
            self.breed = breed

    with pytest.raises(_a(AttributeError)):
        Forgetful("Rex", "lab").name


def test_a_sibling_calls_super_init_too():
    """Implement Cat.__init__ above. 1. Call super().__init__(name) so Animal stores the name. 2. Store indoor on self as self.indoor. Same shape as Dog.__init__, different second attribute."""
    cat = Cat("Tom", True)
    assert cat.name == "Tom"
    assert cat.indoor is True
    assert cat.eat("fish") == "Tom eats fish"


def test_a_sibling_overrides_in_its_own_way():
    """Implement Cat.speak above. 1. Return the string "meow". Dog and Cat each override speak without touching each other or Animal."""
    assert Cat("Tom", True).speak() == "meow"
    assert Dog("Rex", "lab").speak() == "woof"
    assert Animal("Generic").speak() == "..."


def test_isinstance_walks_up_issubclass_too():
    """A Dog is an Animal, so isinstance says yes for every class in its MRO. issubclass asks the same question of the class itself."""
    dog = Dog("Rex", "lab")
    assert isinstance(dog, Animal) is _a(True)
    assert issubclass(Dog, Animal) is _a(True)
    assert issubclass(Animal, Dog) is False


def test_isinstance_accepts_a_tuple():
    """Pass a tuple of classes and isinstance answers whether x is an instance of any of them."""
    dog = Dog("Rex", "lab")
    assert isinstance(dog, (Cat, Dog)) is _a(True)
    assert isinstance("Rex", (int, float)) is _a(False)


def test_object_is_the_root():
    """Every class inherits from object even when you write no parent. __mro__ is a tuple of classes, most specific first."""
    assert Animal.__mro__ == _a((Animal, object))
    assert Dog.__mro__ == _a((Dog, Animal, object))


def test_calling_the_parent_explicitly():
    """Chapter 01 said dog.speak() is Dog.speak(dog). Name a different class and lookup starts there instead, so Animal.speak(dog) skips the override."""
    dog = Dog("Rex", "lab")
    assert dog.speak() == _a("woof")
    assert Animal.speak(dog) == _a("...")


def test_multiple_inheritance_reads_left_to_right():
    """class C(A, B) searches C, then A, then B. When both parents define who, the leftmost wins."""

    class A:
        def who(self):
            return "A"

    class B:
        def who(self):
            return "B"

    class C(A, B):
        pass

    assert C().who() == _a("A")
    assert [cls.__name__ for cls in C.__mro__] == _a(["C", "A", "B", "object"])


def test_mixins_add_one_ability():
    """Implement JsonMixin.to_json above. 1. vars(self) is the dict of this instance's attributes, as chapter 01 showed. 2. Return json.dumps of that dict, which writes it out as a JSON string such as {"name": "Tweety"}. A mixin has no __init__ and no state of its own; listing it first among the parents adds that one method to any class."""
    bird = Bird("Tweety")
    assert bird.to_json() == '{"name": "Tweety"}'
    assert bird.speak() == "..."
    assert [cls.__name__ for cls in Bird.__mro__] == ["Bird", "JsonMixin", "Animal", "object"]


def test_the_diamond_visits_each_class_once():
    """B and C both lead to A. A naive depth-first walk would give D, B, A, C, A. Python lists A once, after every class that inherits from it."""

    class A:
        pass

    class B(A):
        pass

    class C(A):
        pass

    class D(B, C):
        pass

    assert [cls.__name__ for cls in D.__mro__] == _a(["D", "B", "C", "A", "object"])


def test_super_follows_the_mro_not_the_parent():
    """Each __init__ calls super().__init__() first, then records its own name. Inside B, super() is the class after B in D's MRO, which is C, not B's parent A. So A records first, then C, then B, then D."""
    order = []

    class A:
        def __init__(self):
            order.append("A")

    class B(A):
        def __init__(self):
            super().__init__()
            order.append("B")

    class C(A):
        def __init__(self):
            super().__init__()
            order.append("C")

    class D(B, C):
        def __init__(self):
            super().__init__()
            order.append("D")

    D()
    assert order == _a(["A", "C", "B", "D"])
