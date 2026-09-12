"""Stacks and queues.

A stack is a pile. You put things on top and take things off the top, so
the last thing in is the first thing out: LIFO. Undo history is a stack.
The operations are push (put on top), pop (take off the top), and peek
(look at the top without taking it).

A queue is a line. You join at the back and leave from the front, so the
first thing in is the first thing out: FIFO. A print queue is a queue. The
operations are enqueue (join at the back) and dequeue (leave from the front).

A Python list is a fine stack: append is push, pop() with no argument is
pop, and both touch only the end of the list, which is cheap. A list is a
poor queue, because removing from the front, pop(0), has to shift every
remaining element one slot left. collections.deque is a list-like thing
that is cheap at both ends, and popleft is the dequeue.

    from collections import deque
    q = deque()
    q.append(1)      # enqueue
    q.popleft()      # dequeue, returns 1

Every structure in the second half is built like the ones here: a class
holding a plain list or a few pointers, with one method per koan. Where a
method is given, read it. Where it is blanked, the meditation lists the
steps. Empty cases raise IndexError, matching what list.pop does.
"""

from collections import deque

import pytest

from conftest import __


class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)


class ListQueue:
    def __init__(self):
        self._items = []

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.pop(0)


class TwoStackQueue:
    """A queue made of two stacks. New items go on the in-stack. Items leave
    from the out-stack, which is refilled by pouring the in-stack over when
    it runs dry, reversing the order so the oldest item ends up on top."""

    def __init__(self):
        self._in = []
        self._out = []

    def enqueue(self, item):
        self._in.append(item)

    def dequeue(self):
        if not self._out:
            while self._in:
                self._out.append(self._in.pop())
        if not self._out:
            raise IndexError("dequeue from empty queue")
        return self._out.pop()


PAIRS = {")": "(", "]": "[", "}": "{"}


def is_balanced(text):
    stack = Stack()
    for char in text:
        if char in "([{":
            stack.push(char)
        elif char in PAIRS:
            if stack.is_empty() or stack.pop() != PAIRS[char]:
                return False
    return stack.is_empty()


def test_push_puts_an_item_on_top():
    """push is given. It appends to the list, so the top of the stack is the end of the list."""
    stack = Stack()
    stack.push("a")
    stack.push("b")
    assert stack._items == ["a", "b"]


def test_pop_takes_the_top_item_off():
    """Implement Stack.pop above. 1. If _items is empty, raise IndexError. 2. Otherwise remove and return the last element of _items. list.pop() with no argument does exactly that."""
    stack = Stack()
    stack.push(1)
    stack.push(2)
    assert stack.pop() == 2
    assert stack.pop() == 1
    with pytest.raises(IndexError):
        stack.pop()


def test_peek_looks_without_taking():
    """Implement Stack.peek above. 1. If _items is empty, raise IndexError. 2. Otherwise return the last element, _items[-1], without removing it."""
    stack = Stack()
    stack.push(1)
    stack.push(2)
    assert stack.peek() == 2
    assert stack.peek() == 2
    assert stack._items == [1, 2]
    with pytest.raises(IndexError):
        Stack().peek()


def test_is_empty_asks_whether_anything_is_there():
    """Implement Stack.is_empty above. 1. Return True when _items has no elements, False otherwise. Compare len(self._items) with 0."""
    stack = Stack()
    assert stack.is_empty() is True
    stack.push(1)
    assert stack.is_empty() is False


def test_len_makes_the_stack_a_sized_object():
    """Implement Stack.__len__ above. 1. Return the number of items in _items. Chapter 02 showed that len then works on the stack itself, and so does truth testing."""
    stack = Stack()
    assert len(stack) == 0
    assert bool(stack) is False
    stack.push(1)
    assert len(stack) == 1
    assert bool(stack) is True


def test_a_stack_matches_brackets():
    """Implement is_balanced above. 1. Make a Stack. 2. For each char in text: if it is an opener ( [ {, push it; if it is a closer, look it up in PAIRS to get the opener it needs, and return False if the stack is empty or the popped item is not that opener. 3. After the loop return whether the stack is empty, since leftover openers mean unclosed brackets."""
    assert is_balanced("()") is True
    assert is_balanced("([]{})") is True
    assert is_balanced("f(x[0])") is True
    assert is_balanced("(]") is False
    assert is_balanced("((") is False
    assert is_balanced("())") is False
    assert is_balanced("") is True


def test_enqueue_joins_at_the_back():
    """enqueue is given. Like push it appends, so the back of the queue is the end of the list and the front is index 0."""
    queue = ListQueue()
    queue.enqueue("a")
    queue.enqueue("b")
    assert queue._items == ["a", "b"]


def test_dequeue_leaves_from_the_front():
    """Implement ListQueue.dequeue above. 1. If _items is empty, raise IndexError. 2. Otherwise remove and return the element at index 0. list.pop(0) does that."""
    queue = ListQueue()
    queue.enqueue(1)
    queue.enqueue(2)
    assert queue.dequeue() == 1
    assert queue.dequeue() == 2
    with pytest.raises(IndexError):
        queue.dequeue()


def test_pop_zero_shifts_everything_so_use_a_deque():
    """Removing index 0 from a list moves every other element down one slot. A deque removes from either end without moving anything."""
    queue = deque()
    queue.append(1)
    queue.append(2)
    queue.appendleft(0)
    assert list(queue) == [0, 1, 2]
    assert queue.popleft() == 0


def test_two_stacks_make_a_queue():
    """Implement TwoStackQueue.dequeue above. 1. If _out is empty, pop every item from _in and append it to _out, so the order reverses and the oldest item is now last in _out. 2. If _out is still empty, raise IndexError. 3. Return _out.pop()."""
    queue = TwoStackQueue()
    queue.enqueue(1)
    queue.enqueue(2)
    assert queue.dequeue() == 1
    queue.enqueue(3)
    assert queue.dequeue() == 2
    assert queue.dequeue() == 3
    with pytest.raises(IndexError):
        queue.dequeue()
