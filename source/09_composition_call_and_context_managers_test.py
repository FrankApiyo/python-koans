"""Composition, __call__, and context managers.

Inheritance says is-a: a Dog is an Animal. Composition says has-a: a Car
has an Engine. When you only want some of another object's behaviour, keep
it as an attribute instead of inheriting from it, and forward the calls
you need. Forwarding a call is called delegation.

    class Car:
        def __init__(self, engine):
            self.engine = engine

        def start(self):
            return self.engine.start()

Forwarding every method by hand is tedious. Python calls
__getattr__(self, name) only when normal attribute lookup fails, so one
__getattr__ that reads name off the wrapped object delegates all the rest.

Two more dunders. __call__ lets an instance be called like a function:
double(5) runs double.__call__(5); callable(x) asks whether x can be called.
__enter__ and __exit__ make an object work in a with statement. with x as y
runs y = x.__enter__(), then the block, then x.__exit__(exc_type, exc, tb),
always, even if the block raised. Those three describe the exception, or
are all None. If __exit__ returns True the exception is swallowed.

contextlib.contextmanager builds the same thing from a generator (chapter
08). Code before its single yield is the enter, the yielded value is what
as binds, code after the yield is the exit. open(path) returns a file
handle with read(), close(), and a closed flag. A test that takes tmp_path
as a parameter is handed an empty folder that pytest deletes afterwards.
"""

import contextlib

import pytest

from conftest import __


class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
        self.running = False

    def start(self):
        self.running = True
        return "vroom"

    def stop(self):
        self.running = False


class Car:
    def __init__(self, engine):
        self.engine = engine

    def start(self):
        # >>> answer
        return self.engine.start()
        # <<<

    def __getattr__(self, name):
        # >>> answer
        return getattr(self.engine, name)
        # <<<


class Echo:
    greeting = "hi"

    def __getattr__(self, name):
        return f"no {name} here"


class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):
        # >>> answer
        return self.factor * value
        # <<<


class Timer:
    def __init__(self):
        self.log = []

    def __enter__(self):
        self.log.append("enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.log.append("exit")
        return False


class Guard:
    """Remembers what __exit__ was told. swallow is what __exit__ returns."""

    def __init__(self, swallow=False):
        self.swallow = swallow
        self.exc_type = None
        self.exc = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exc_type = exc_type
        self.exc = exc
        return self.swallow


@contextlib.contextmanager
def opened(path):
    # >>> answer
    handle = open(path)
    try:
        yield handle
    finally:
        handle.close()
    # <<<


class Connection:
    def __init__(self):
        self.open = True

    def close(self):
        self.open = False


def test_a_car_has_an_engine():
    """Car stores the Engine it was given. The car is not an engine; it owns one. That is has-a, not is-a."""
    engine = Engine(horsepower=90)
    car = Car(engine)
    assert (car.engine is engine) is _a(True)
    assert isinstance(car, Engine) is _a(False)


def test_start_delegates_to_the_engine():
    """Implement Car.start above. 1. Call self.engine.start() and return whatever it returns. The car does not know how to start; it asks the part that does."""
    engine = Engine(horsepower=90)
    car = Car(engine)
    assert car.start() == "vroom"
    assert engine.running is True


def test_getattr_is_the_fallback_for_missing_names():
    """Python calls __getattr__ only after the normal lookup fails. greeting exists, so it never reaches __getattr__; anything else does."""
    echo = Echo()
    assert echo.greeting == _a("hi")
    assert echo.anything == _a("no anything here")


def test_getattr_delegates_everything_else_to_the_engine():
    """Implement Car.__getattr__ above. 1. Return getattr(self.engine, name), the builtin that reads an attribute by its string name. engine and start live on the car, so they never reach __getattr__; horsepower and stop do."""
    engine = Engine(horsepower=90)
    car = Car(engine)
    assert car.horsepower == 90
    car.start()
    car.stop()
    assert engine.running is False
    with pytest.raises(AttributeError):
        car.wings


def test_callable_asks_whether_something_can_be_called():
    """Functions and classes are callable; calling a class makes an instance. A plain instance is not, because its class has no __call__."""
    assert callable(Engine) is _a(True)
    assert callable(Engine(90)) is _a(False)


def test_call_makes_an_instance_callable():
    """Implement Multiplier.__call__ above. 1. Return self.factor times value. Python turns double(5) into double.__call__(5), so the instance can go anywhere a function can."""
    double = Multiplier(2)
    assert callable(double) is True
    assert double(5) == 10
    assert [double(n) for n in [1, 2, 3]] == [2, 4, 6]


def test_with_calls_enter_before_the_block_and_exit_after():
    """as binds whatever __enter__ returns, here the Timer itself. The block runs between enter and exit."""
    with Timer() as timer:
        timer.log.append("block")
    assert timer.log == _a(["enter", "block", "exit"])
    assert isinstance(timer, Timer) is _a(True)


def test_exit_receives_the_exception():
    """When the block raises, __exit__ still runs and is told the exception's class and the exception itself. Returning False lets it carry on out of the with."""
    guard = Guard(swallow=False)
    with pytest.raises(ValueError):
        with guard:
            raise ValueError("boom")
    assert guard.exc_type is _a(ValueError)
    assert str(guard.exc) == _a("boom")


def test_returning_true_from_exit_swallows_the_exception():
    """A true return from __exit__ means handled: the code after the with runs as if nothing happened. When the block raised nothing, all three arguments are None."""
    with Guard(swallow=True) as quiet:
        raise ValueError("boom")
    assert quiet.exc_type is _a(ValueError)
    with Guard(swallow=False) as calm:
        pass
    assert calm.exc_type is _a(None)


def test_contextmanager_turns_a_generator_into_a_context_manager(tmp_path):
    """Implement opened above. 1. Open the file with open(path) and keep the handle. 2. Inside a try, yield the handle; the with block runs there. 3. In the finally, call handle.close(), so the file closes even when the block raises."""
    path = tmp_path / "note.txt"
    path.write_text("hello")
    with opened(path) as handle:
        assert handle.read() == "hello"
        assert handle.closed is False
    assert handle.closed is True
    with pytest.raises(ValueError):
        with opened(path) as handle:
            raise ValueError("boom")
    assert handle.closed is True


def test_closing_calls_close_on_exit():
    """contextlib.closing wraps any object that has a close method. Its __enter__ returns the object and its __exit__ calls close, for things that were written without __enter__ and __exit__."""
    with contextlib.closing(Connection()) as conn:
        assert conn.open is _a(True)
    assert conn.open is _a(False)
