r"""Heaps.

A min-heap is a binary tree with one rule: every parent is no larger than
its children. Nothing else is promised about the order, but that rule alone
puts the smallest item at the root, and keeps every change to a short walk
between the root and a leaf. A heap keeps its tree in a plain list, row by
row from the top, left to right. This heap

            1                   index:  0  1  2  3  4
           / \                  value:  1  3  2  7  4
          3   2
         / \                    parent of i  = (i - 1) // 2
        7   4                   left child   = 2 * i + 1
                                right child  = 2 * i + 2

is the list [1, 3, 2, 7, 4], and the arrows are arithmetic on indexes.
Pushing appends at the end, the next free leaf, then swaps the item upward
past any larger parent: sifting up. Popping moves the last item into index
0, then swaps it downward past any smaller child: sifting down. The
standard library's heapq module does both on an ordinary list:

    import heapq
    h = []
    heapq.heappush(h, 3)
    heapq.heappush(h, 1)
    heapq.heappop(h)      # 1, the smallest

MinHeap below builds the same thing by hand, one method per koan.
"""

import heapq

import pytest

from conftest import __


class MinHeap:
    def __init__(self):
        self._items = []

    def _parent(self, i):
        return (i - 1) // 2

    def _left(self, i):
        return 2 * i + 1

    def _right(self, i):
        return 2 * i + 2

    def push(self, item):
        self._items.append(item)
        self._sift_up(len(self._items) - 1)

    def _sift_up(self, i):
        while i > 0 and self._items[i] < self._items[self._parent(i)]:
            parent = self._parent(i)
            self._items[i], self._items[parent] = self._items[parent], self._items[i]
            i = parent

    def _sift_down(self, i):
        __()

    def pop(self):
        __()

    def peek(self):
        __()


def k_smallest(items, k):
    __()


def test_the_tree_lives_in_a_list():
    """The heap in the lesson. Index 1 holds 3; its children sit at 2 * 1 + 1 and 2 * 1 + 2. Walk the formulas backwards to find a parent."""
    heap = MinHeap()
    heap._items = [1, 3, 2, 7, 4]
    assert heap._items[heap._left(1)] == __
    assert heap._parent(4) == __


def test_every_parent_is_no_larger_than_its_children():
    """The heap rule, checked at index 3: its parent is index 1. Because the rule holds at every index, the smallest item is always at the root."""
    heap = MinHeap()
    heap._items = [1, 3, 2, 7, 4]
    assert heap._items[heap._parent(3)] == __
    assert min(heap._items) == heap._items[__]


def test_push_sifts_the_new_item_up():
    """push and _sift_up are given. Each push appends, then swaps the new item with its parent while it is smaller. Trace the four pushes: 1 lands at index 3, passes 5, then passes 3."""
    heap = MinHeap()
    heap.push(5)
    heap.push(3)
    heap.push(8)
    heap.push(1)
    assert heap._items == __
    assert heap._items[0] == __


def test_sift_down_moves_an_item_below_its_children():
    """Implement MinHeap._sift_down above. 1. Loop forever. 2. Let smallest = i. For each child index, _left(i) and _right(i): if it is less than len(self._items) and its item is less than the item at smallest, set smallest to that child index. 3. If smallest is still i, return. 4. Otherwise swap the items at i and smallest, as _sift_up does, set i = smallest, and go round again."""
    heap = MinHeap()
    heap._items = [9, 1, 2, 3, 4]
    heap._sift_down(0)
    assert heap._items == [1, 3, 2, 9, 4]
    heap._items = [1, 2, 3]
    heap._sift_down(0)
    assert heap._items == [1, 2, 3]


def test_pop_returns_the_smallest_item():
    """Implement MinHeap.pop above. 1. If _items is empty, raise IndexError. 2. Swap _items[0] with _items[-1]. 3. Remove the last item with list.pop() and keep it; it is the old root. 4. If any items remain, call self._sift_down(0). 5. Return the kept item."""
    heap = MinHeap()
    heap.push(5)
    heap.push(3)
    heap.push(8)
    heap.push(1)
    assert heap.pop() == 1
    assert heap.pop() == 3
    assert heap.pop() == 5
    assert heap.pop() == 8
    with pytest.raises(IndexError):
        heap.pop()


def test_peek_shows_the_smallest_without_removing_it():
    """Implement MinHeap.peek above. 1. If _items is empty, raise IndexError. 2. Return _items[0], the root, without removing it."""
    heap = MinHeap()
    heap.push(4)
    heap.push(2)
    assert heap.peek() == 2
    assert heap.peek() == 2
    assert len(heap._items) == 2
    with pytest.raises(IndexError):
        MinHeap().peek()


def test_heapq_does_the_same_on_a_plain_list():
    """heapq has no class. heappush and heappop take an ordinary list and keep it in heap order, so index 0 is always the smallest."""
    h = []
    heapq.heappush(h, 5)
    heapq.heappush(h, 3)
    heapq.heappush(h, 8)
    heapq.heappush(h, 1)
    assert h[0] == __
    assert [heapq.heappop(h) for _ in range(4)] == __


def test_k_smallest_pops_k_times():
    """Implement k_smallest above. 1. Make an empty list called heap. 2. heapq.heappush every element of items onto it. 3. Return a list of k heapq.heappop results, in the order they come out."""
    assert k_smallest([9, 4, 7, 1, 8, 2], 3) == [1, 2, 4]
    assert k_smallest([5], 1) == [5]
    assert k_smallest([3, 1, 2], 0) == []


def test_tuples_make_a_priority_queue():
    """Tuples compare by their first element, then the second on a tie. Put the priority first and the heap hands back the most urgent task."""
    tasks = []
    heapq.heappush(tasks, (2, "write"))
    heapq.heappush(tasks, (1, "plan"))
    heapq.heappush(tasks, (3, "ship"))
    assert heapq.heappop(tasks) == __
    assert heapq.heappop(tasks)[1] == __
