"""pytest: mocks, patches, and the boundary.

A test wants to know what the code under test did without running the
whole world behind it. In a web application a save handler does not do the
slow work itself; it calls task.delay(pk), which puts the task on a queue
for a worker somewhere else and returns at once. The handler's test does
not want the queue, the worker, or the task. It wants to know what the
handler handed over. A mock is an object that stands in for the real thing
and remembers every call it receives, so the test can ask afterwards: were
you called, how many times, with what.

unittest.mock.MagicMock() accepts any call, any attribute, any method, and
records all of it. After m(1, 2), m.called is True, m.call_count is 1 and
m.call_args.args is (1, 2). A call returns another MagicMock unless you set
m.return_value, and m.side_effect can be an exception to raise or a
function to run instead. m.assert_called_once_with(1, 2) raises
AssertionError when the recording says otherwise, and assert_not_called
is the same question the other way round. An assertion on a mock is never
a claim about what the real task would have done. It is a claim about what
the code under test sent to it. What the task does when it runs is proved
by the task's own tests, elsewhere.

patch swaps one name for a mock while a block runs, then puts the original
back. patch("koan_tasks.decrypt.delay") takes a string because patch
imports the module the string starts with and walks the dots: import
koan_tasks, then its decrypt, then its delay. The string must name the
place the code under test looks the name up at call time; a reference
captured earlier keeps pointing at the real function, which is why
from-imports are patched in the importing module. patch.object(obj, "name")
is the same swap from an object you already hold, and a third argument
replaces with a value of your choosing instead of a MagicMock. Used as a
decorator, patch wraps the whole test and passes the mock in as an extra
argument. Stacked decorators arrive bottom up: the one nearest the def
fills the first argument. *_mocks catches the rest, which are patched only
to be silenced.

A bare MagicMock accepts any arguments, so a wrong call passes;
autospec=True gives it the real signature. mock_calls lists every call to
a mock and to its attributes, in order. A coroutine cannot be replaced by a
MagicMock because await needs an awaitable, and a MagicMock is not one;
AsyncMock returns a coroutine from each call, and assert_awaited_once_with
checks it was awaited. pytest's monkeypatch fixture is the same swap
without the mock: monkeypatch.setattr(obj, "name", value) is undone when
the test ends.

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

import asyncio
import sys
import types
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from conftest import __


def _make_tasks_module():
    """A module built by hand, so patch can reach it through the string "koan_tasks"."""
    module = types.ModuleType("koan_tasks")
    module.queued = []

    class Task:
        def __init__(self, name):
            self.name = name

            def delay(pk):
                module.queued.append((name, pk))

            self.delay = delay

    module.save_json = Task("save_json")
    module.update_date_modified = Task("update_date_modified")
    module.decrypt = Task("decrypt")
    sys.modules[module.__name__] = module
    return module


tasks = _make_tasks_module()


@dataclass
class Instance:
    pk: int
    encrypted: bool = False


@dataclass
class Settings:
    auto_decrypt: bool = False


def post_save(instance, settings):
    # >>> answer
    if settings.auto_decrypt and instance.encrypted:
        tasks.decrypt.delay(instance.pk)
        return
    tasks.save_json.delay(instance.pk)
    tasks.update_date_modified.delay(instance.pk)
    # <<<


def old_post_save(instance, settings):
    tasks.save_json.delay(instance.pk)
    tasks.update_date_modified.delay(instance.pk)
    if settings.auto_decrypt and instance.encrypted:
        tasks.decrypt.delay(instance.pk)


async def save_json_after(pk, decrypt):
    await decrypt(pk)
    tasks.save_json.delay(pk)


def test_a_mock_accepts_any_call_and_remembers_it():
    """A MagicMock takes whatever arguments it is given and records them. called, call_count and call_args are that recording, read back after the fact."""
    m = MagicMock()
    m(1, key="two")
    assert m.called is _a(True)
    assert m.call_count == _a(1)
    assert m.call_args.args == _a((1,))
    assert m.call_args.kwargs == _a({"key": "two"})


def test_a_mock_returns_a_mock_unless_told_what_to_return():
    """A call on a mock hands back another mock, so code that uses the result keeps going. return_value replaces that with a value of your choosing."""
    m = MagicMock()
    assert isinstance(m(), MagicMock) is _a(True)
    m.return_value = 42
    assert m() == _a(42)


def test_side_effect_raises_or_computes_instead():
    """side_effect set to an exception makes every call raise it. Set to a function, the call runs that function with the same arguments and returns its result."""
    m = MagicMock(side_effect=ValueError("no"))
    with pytest.raises(_a(ValueError)):
        m()
    m.side_effect = lambda x: x * 2
    assert m(3) == _a(6)


def test_assert_called_once_with_is_a_question_put_to_the_recording():
    """The assertion reads the recording, not the real thing. Different arguments, or a second call, make it raise AssertionError, which is what makes it a test."""
    m = MagicMock()
    m("a")
    m.assert_called_once_with("a")
    with pytest.raises(_a(AssertionError)):
        m.assert_called_once_with("b")
    m("a")
    with pytest.raises(_a(AssertionError)):
        m.assert_called_once_with("a")


def test_mock_calls_keeps_the_order_across_attributes():
    """Every call to a mock or to any attribute of it lands on mock_calls in order. call.decrypt(1) is how you spell the expected entry. This is how a test proves one thing happened after another."""
    worker = MagicMock()
    worker.decrypt(1)
    worker.save_json(1)
    assert worker.mock_calls == _a([call.decrypt(1), call.save_json(1)])
    assert worker.save_json.call_count == _a(1)


def test_patch_swaps_a_name_for_the_block_and_puts_it_back():
    """Inside the with block the attribute is the mock that as names. When the block ends the original is back, and nothing else about the object has changed."""
    original = tasks.save_json.delay
    with patch.object(tasks.save_json, "delay") as fake:
        inside = tasks.save_json.delay
    assert (inside is fake) is _a(True)
    assert (tasks.save_json.delay is original) is _a(True)


def test_the_string_target_is_a_module_then_its_attributes():
    """patch imports koan_tasks and walks the dots to decrypt, then delay. The call reaches the mock and stops there: the real delay never runs, so nothing is queued. A mock is a wall, and the test asserts what arrived at the wall."""
    with patch.object(tasks, "queued", []) as queued:
        with patch("koan_tasks.decrypt.delay") as fake:
            tasks.decrypt.delay(7)
    assert fake.call_args.args == _a((7,))
    assert queued == _a([])


def test_patch_the_name_the_code_looks_up_not_the_one_you_captured():
    """A reference taken before the patch still points at the real function, and calling it queues real work while the mock sees nothing. Patch the place the code under test looks the name up when it runs."""
    captured = tasks.decrypt.delay
    with patch.object(tasks, "queued", []) as queued:
        with patch("koan_tasks.decrypt.delay") as fake:
            captured(7)
    assert fake.called is _a(False)
    assert queued == _a([("decrypt", 7)])


@patch("koan_tasks.decrypt.delay")
def test_a_decorator_patch_hands_the_mock_to_the_test(mock_decrypt):
    """As a decorator, patch wraps the whole test in the with block and passes the mock as an argument. The argument's name is yours to choose; its position is what matters."""
    assert (tasks.decrypt.delay is mock_decrypt) is _a(True)
    assert isinstance(mock_decrypt, MagicMock) is _a(True)


@patch("koan_tasks.save_json.delay")
@patch("koan_tasks.decrypt.delay")
def test_stacked_patches_arrive_bottom_up(first, second):
    """Decorators apply from the bottom, so the patch nearest the def fills the first argument. Calling decrypt.delay shows which mock is which."""
    tasks.decrypt.delay(1)
    assert first.call_args.args == _a((1,))
    assert second.called is _a(False)


@patch("koan_tasks.update_date_modified.delay")
@patch("koan_tasks.save_json.delay")
@patch("koan_tasks.decrypt.delay")
def test_star_mocks_catches_the_patches_you_do_not_ask_about(mock_decrypt, *_mocks):
    """Some patches exist only so the real thing does not run. Catching them in *_mocks says exactly that: silenced, not asserted. Only the first argument is named because only it is examined."""
    assert len(_mocks) == _a(2)
    assert (mock_decrypt is tasks.decrypt.delay) is _a(True)


@patch("koan_tasks.update_date_modified.delay")
@patch("koan_tasks.save_json.delay")
@patch("koan_tasks.decrypt.delay")
def test_post_save_queues_decryption_instead_of_the_json_task(mock_decrypt, mock_save_json, *_mocks):
    """Implement post_save above. 1. If settings.auto_decrypt and instance.encrypted are both true, call tasks.decrypt.delay(instance.pk) and return. 2. Otherwise call tasks.save_json.delay(instance.pk), then tasks.update_date_modified.delay(instance.pk). The mocks prove which branch ran by what reached them, and assert_not_called is as much a claim as assert_called_once_with."""
    post_save(Instance(pk=5, encrypted=True), Settings(auto_decrypt=True))
    mock_decrypt.assert_called_once_with(5)
    mock_save_json.assert_not_called()

    post_save(Instance(pk=6, encrypted=False), Settings(auto_decrypt=True))
    mock_decrypt.assert_called_once_with(5)
    mock_save_json.assert_called_once_with(6)


def test_the_same_handler_unpatched_puts_real_work_on_the_queue():
    """Take the mocks away and delay does what it always did. The patched koan was never about the queue; it was about what the handler chose to send there, and this one checks the queue itself."""
    with patch.object(tasks, "queued", []) as queued:
        post_save(Instance(pk=5, encrypted=True), Settings(auto_decrypt=True))
        post_save(Instance(pk=6), Settings())
    assert queued == _a([("decrypt", 5), ("save_json", 6), ("update_date_modified", 6)])


@patch("koan_tasks.update_date_modified.delay")
@patch("koan_tasks.save_json.delay")
@patch("koan_tasks.decrypt.delay")
def test_the_red_test_fails_against_the_old_handler(mock_decrypt, mock_save_json, *_mocks):
    """old_post_save is the handler before the fix: it queues the json task as well as decryption. Run the fixed handler's assertions against it and assert_not_called is the one that catches the bug. A test that cannot fail proves nothing."""
    old_post_save(Instance(pk=5, encrypted=True), Settings(auto_decrypt=True))
    mock_decrypt.assert_called_once_with(5)
    with pytest.raises(_a(AssertionError)):
        mock_save_json.assert_not_called()


def test_autospec_refuses_what_the_real_signature_refuses():
    """A bare MagicMock accepts any arguments, so a call with the wrong number of them passes and a typo in the handler goes unnoticed. autospec=True gives the mock the real signature, and the same wrong call raises TypeError."""
    with patch.object(tasks.save_json, "delay") as loose:
        loose(1, 2, 3)
    with patch.object(tasks.save_json, "delay", autospec=True) as strict:
        strict(1)
        with pytest.raises(_a(TypeError)):
            strict(1, 2, 3)
    assert loose.call_count == _a(1)


def test_a_magic_mock_cannot_be_awaited():
    """save_json_after awaits whatever it is given. A MagicMock call returns a MagicMock, and awaiting one is a TypeError. That error is the sign that the code under test is async and the double must be an AsyncMock."""
    with pytest.raises(_a(TypeError)):
        asyncio.run(save_json_after(9, MagicMock()))


def test_async_mock_returns_a_coroutine_from_each_call():
    """AsyncMock records the call the way MagicMock does, and its result can be awaited. assert_awaited_once_with proves the coroutine was driven, not merely created, and the plain patch on delay proves what ran after it."""
    fake_decrypt = AsyncMock()
    with patch("koan_tasks.save_json.delay") as mock_save_json:
        asyncio.run(save_json_after(9, fake_decrypt))
    fake_decrypt.assert_awaited_once_with(9)
    assert fake_decrypt.await_count == _a(1)
    assert mock_save_json.call_args.args == _a((9,))


def test_monkeypatch_is_pytests_own_swap(monkeypatch):
    """The monkeypatch fixture sets an attribute for one test and restores it afterwards. It is patch without the mock: you choose the replacement, here a function that records into a list."""
    seen = []
    monkeypatch.setattr(tasks.decrypt, "delay", seen.append)
    tasks.decrypt.delay(3)
    tasks.decrypt.delay(4)
    assert seen == _a([3, 4])
