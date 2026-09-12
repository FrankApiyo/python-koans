"""Linked lists.

A Python list keeps its items side by side in one block, so item 3 is
found by jumping straight to slot 3. A linked list keeps each item in its
own small object, a node, and every node holds a pointer to the next one.
To reach item 3 you start at the first node and follow the pointers.

    head
     |
     v
    [1 | next] --> [2 | next] --> [3 | next] --> None

    class Node:
        def __init__(self, value, next=None):
            self.value = value
            self.next = next

    third = Node(3)
    second = Node(2, third)
    first = Node(1, second)
    first.next.next.value     # 3

The list itself is one pointer, head, to the first node, or None when the
list is empty. The last node's next is None, which is how a walk knows to
stop. Every operation is a walk: start at head, follow next until you find
what you want or reach None. Changing the list means changing pointers,
not moving items. Splicing a node in after one you already hold is two
assignments however long the list is, where a Python list would shift
every later item along by one slot.

LinkedList below is built one method at a time. value and next are plain
attributes on Node, so read and assign them freely.
"""

import pytest

from conftest import __


class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next


class LinkedList:
    def __init__(self):
        self.head = None

    def push_front(self, value):
        self.head = Node(value, self.head)

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def __len__(self):
        count = 0
        for _ in self:
            count += 1
        return count

    def append(self, value):
        if self.head is None:
            self.head = Node(value)
            return
        node = self.head
        while node.next is not None:
            node = node.next
        node.next = Node(value)

    def find(self, value):
        node = self.head
        while node is not None:
            if node.value == value:
                return node
            node = node.next
        return None

    def insert_after(self, node, value):
        node.next = Node(value, node.next)

    def remove(self, value):
        prev = None
        node = self.head
        while node is not None:
            if node.value == value:
                if prev is None:
                    self.head = node.next
                else:
                    prev.next = node.next
                return
            prev = node
            node = node.next
        raise ValueError(f"{value!r} is not in the list")

    def reverse(self):
        prev = None
        current = self.head
        while current is not None:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev

    def __repr__(self):
        return f"LinkedList({list(self)!r})"


class DoublyLinkedNode:
    """A node that points both ways. next leads forward and prev leads back."""

    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None


def test_a_node_holds_a_value_and_points_to_the_next_node():
    """A Node is two attributes. value is the item; next is the following Node, or None at the end of the chain."""
    last = Node(2)
    first = Node(1, last)
    assert first.next is last
    assert first.next.value == 2
    assert last.next is None


def test_push_front_makes_the_new_node_the_head():
    """push_front is given. It builds a Node whose next is the old head, then points head at it, so the newest value is always first."""
    ll = LinkedList()
    ll.push_front(1)
    ll.push_front(2)
    assert ll.head.value == 2
    assert ll.head.next.value == 1
    assert ll.head.next.next is None


def test_iter_walks_the_chain_from_head():
    """Implement LinkedList.__iter__ above. 1. Set node = self.head. 2. while node is not None: yield node.value, then node = node.next. Chapter 08 showed that a method with yield is a generator, so for works on the list."""
    ll = LinkedList()
    ll.push_front(3)
    ll.push_front(2)
    ll.push_front(1)
    seen = []
    for value in ll:
        seen.append(value)
    assert seen == [1, 2, 3]
    for value in LinkedList():
        seen.append(value)
    assert seen == [1, 2, 3]


def test_len_counts_by_walking():
    """Implement LinkedList.__len__ above. 1. Set count = 0. 2. for each value in self, add 1 to count. 3. Return count. Nothing stores the size, so len is O(n) here where a list's len is O(1)."""
    ll = LinkedList()
    assert len(ll) == 0
    ll.push_front(1)
    ll.push_front(2)
    assert len(ll) == 2
    assert list(ll) == [2, 1]


def test_append_walks_to_the_last_node():
    """Implement LinkedList.append above. 1. If head is None, set head = Node(value) and return. 2. Otherwise set node = self.head and, while node.next is not None, set node = node.next, so you stop on the last node. 3. Set node.next = Node(value)."""
    ll = LinkedList()
    ll.append(1)
    assert ll.head.value == 1
    ll.append(2)
    ll.push_front(0)
    assert list(ll) == [0, 1, 2]


def test_find_returns_the_node_holding_a_value():
    """Implement LinkedList.find above. 1. Walk as __iter__ does, node = self.head then node = node.next, but keep the node rather than yielding its value. 2. If node.value == value, return node. 3. After the loop return None."""
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    node = ll.find(2)
    assert node.value == 2
    assert node is ll.head.next
    assert ll.find(9) is None


def test_insert_after_splices_in_a_node():
    """Implement LinkedList.insert_after above. 1. Set node.next = Node(value, node.next), so the new node points at whatever node used to point at and node now points at the new node. One assignment, no walking."""
    ll = LinkedList()
    ll.append(1)
    ll.append(3)
    ll.insert_after(ll.find(1), 2)
    assert list(ll) == [1, 2, 3]
    ll.insert_after(ll.find(3), 4)
    assert list(ll) == [1, 2, 3, 4]


def test_remove_unlinks_the_first_node_with_a_value():
    """Implement LinkedList.remove above. 1. Set prev = None and node = self.head. 2. while node is not None: if node.value == value, unlink it and return: when prev is None the match is the head, so set self.head = node.next, otherwise set prev.next = node.next. If it does not match, set prev = node and node = node.next. 3. After the loop raise ValueError, as list.remove does."""
    ll = LinkedList()
    for value in [1, 2, 3]:
        ll.append(value)
    ll.remove(2)
    assert list(ll) == [1, 3]
    ll.remove(1)
    assert list(ll) == [3]
    assert ll.head.value == 3
    with pytest.raises(ValueError):
        ll.remove(9)


def test_reverse_turns_every_arrow_around():
    """Implement LinkedList.reverse above. 1. Set prev = None and current = self.head. 2. while current is not None: save next_node = current.next, point current.next at prev, move prev to current, move current to next_node. 3. After the loop prev is the old last node, so set self.head = prev."""
    ll = LinkedList()
    for value in [1, 2, 3]:
        ll.append(value)
    ll.reverse()
    assert list(ll) == [3, 2, 1]
    assert ll.find(1).next is None
    empty = LinkedList()
    empty.reverse()
    assert list(empty) == []


def test_repr_leans_on_iter():
    """__repr__ is given. list(self) calls __iter__, so the one generator method gives the list a readable repr for free."""
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    assert repr(ll) == "LinkedList([1, 2])"


def test_a_doubly_linked_node_points_both_ways():
    """Give each node a prev pointer too and you can walk backwards, and unlink a node you hold without searching for the one before it: node.prev.next = node.next. The cost is one more pointer to keep in step on every change."""
    a = DoublyLinkedNode(1)
    b = DoublyLinkedNode(2)
    a.next = b
    b.prev = a
    assert b.prev.value == 1
    assert a.prev is None


def test_when_a_linked_list_beats_a_list():
    """Splicing at a node you already hold is two pointer changes however long the list, O(1), where a list shifts every later item, O(n). Reaching the nth item is the other way round: a walk of n steps against one jump. Choose by the operation you do most."""
    ll = LinkedList()
    for value in range(1000):
        ll.append(value)
    middle = ll.find(500)
    ll.insert_after(middle, "new")
    assert middle.next.value == "new"
    cost = {"insert after a node you hold": "O(1)", "reach the nth item": "O(n)"}
    assert cost["reach the nth item"] == "O(n)"
