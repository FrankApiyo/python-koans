"""Recursion.

A recursive function is one that calls itself. That only works if some
input makes it stop without calling itself, the base case, and every other
input moves one step closer to it, the recursive case.

    def countdown(n):
        if n == 0:               # base case
            return ["liftoff"]
        return [n] + countdown(n - 1)   # recursive case

    countdown(3)     # [3, 2, 1, 'liftoff']

Each call gets its own frame: a fresh set of local variables, plus a note
of where to continue once the call returns. Frames live on a stack, the
one from chapter 11. countdown(3) pushes a frame, calls countdown(2) which
pushes another on top, and so on down to countdown(0). Only then do the
frames pop, top first, each one finishing its own [n] + ... as the answer
comes back up. Three frames are waiting while the base case runs.

The stack is not unlimited. Python lets it grow to about a thousand frames
and then raises RecursionError, which is what a missing base case looks
like in practice.

Every recursive function in this file is written the same way. Name the
base case first. Then make the recursive call on a smaller piece of the
problem and trust it to return the right answer for that piece.
"""

import functools
import sys

import pytest

from conftest import __


def countdown(n):
    if n == 0:
        return ["liftoff"]
    return [n] + countdown(n - 1)


def factorial(n):
    __()


def sum_list(items):
    __()


def forever(n):
    return forever(n + 1)


class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next


def length(node):
    __()


def fib(n):
    __()


def power_set(items):
    __()


def test_a_recursive_function_stops_at_its_base_case():
    """countdown is given. Each call builds its answer from the call below it, and the base case is the only frame that returns without asking anyone."""
    assert countdown(0) == __
    assert countdown(3) == __


def test_factorial_multiplies_down_to_one():
    """Implement factorial above. 1. Base case: if n is 0, return 1. 2. Otherwise return n times factorial of n - 1. factorial(3) is 3 * 2 * 1 * 1."""
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120


def test_sum_list_peels_off_the_first_item():
    """Implement sum_list above. 1. Base case: if items is empty, return 0. 2. Otherwise return items[0] plus sum_list of the rest, items[1:]. Each call handles one item and hands the shorter list down."""
    assert sum_list([]) == 0
    assert sum_list([4]) == 4
    assert sum_list([1, 2, 3, 4]) == 10


def test_no_base_case_means_no_end_until_the_stack_is_full():
    """forever never stops, so frames pile up until Python refuses to push another. sys.getrecursionlimit() says how many it allows; the default is 1000."""
    assert sys.getrecursionlimit() == __
    with pytest.raises(__):
        forever(0)


def test_length_of_a_chain_of_nodes():
    """Implement length above. 1. Base case: if node is None, return 0. 2. Otherwise return 1 plus the length of node.next. A chain of nodes is a smaller chain with one node in front."""
    assert length(None) == 0
    assert length(Node("a")) == 1
    assert length(Node("a", Node("b", Node("c")))) == 3


def test_fib_calls_itself_twice():
    """Implement fib above. 1. Base case: if n is less than 2, return n, so fib(0) is 0 and fib(1) is 1. 2. Otherwise return fib(n - 1) plus fib(n - 2). Two recursive calls, not one."""
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(10) == 55


def test_naive_fib_does_the_same_work_over_and_over():
    """fib(20) calls fib(18) twice, fib(17) three times, and so on down. fib_counted is fib with one extra line that appends to calls, so len(calls) is the number of frames ever pushed."""
    calls = []

    def fib_counted(n):
        calls.append(n)
        if n < 2:
            return n
        return fib_counted(n - 1) + fib_counted(n - 2)

    fib_counted(5)
    assert len(calls) == __
    calls.clear()
    fib_counted(20)
    assert len(calls) == __


def test_lru_cache_remembers_every_answer():
    """functools.lru_cache is a decorator, written above a def like @classmethod in chapter 04. It stores each argument's return value and hands it back next time without running the body, so every n is computed once."""
    calls = []

    @functools.lru_cache
    def fib_cached(n):
        calls.append(n)
        if n < 2:
            return n
        return fib_cached(n - 1) + fib_cached(n - 2)

    assert fib_cached(20) == 6765
    assert len(calls) == __
    assert fib_cached(80) == __


def test_power_set_lists_every_subset():
    """Implement power_set above. 1. Base case: if items is empty, return [[]], a list holding the one empty subset. 2. Otherwise compute the power set of items[1:], the subsets without the first item. 3. Build a second list by putting items[0] in front of each of those subsets. 4. Return the first list followed by the second."""
    assert power_set([]) == [[]]
    assert power_set([1]) == [[], [1]]
    subsets = power_set([1, 2, 3])
    assert len(subsets) == 8
    assert sorted(subsets) == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
