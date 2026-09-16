"""Searching and sorting.

Searching asks where something is. Linear search walks the list from the
front and checks every item, so it takes n steps for n items and works on
any list. Binary search needs a sorted list and uses that: look at the
middle item; if it is smaller than the target, the target can only be in
the right half, if bigger, only in the left half, so each look throws away
half the list. That is log2(n) steps: about 20 looks for a million items.

Sorting puts a list in order. Python has sorted, which returns a new sorted
list, and list.sort, which reorders the list in place. Every sorting
function you write in this chapter behaves like sorted: it takes a list,
returns a new sorted list, and leaves the input exactly as it was.

    sorted([3, 1, 2])              # [1, 2, 3]
    sorted(["bb", "a"], key=len)   # ['a', 'bb']

key is a function called once per item; what it returns decides the order,
and the original items are what comes out. A sort is stable when items
whose keys are equal keep the order they arrived in. sorted is stable.

Every comparison in this file is a < b. Chapter 02 showed that a class only
needs __lt__ for that, so any sort here can order your own objects.

Bubble sort and insertion sort are simple and quadratic: about n * n steps.
Merge sort and quick sort split the list and recurse, as in chapter 13, and
take about n * log2(n) steps, which is why they are the ones used in
practice.

Picture: lessons/svg/14_binary_search.svg and 14_merge_sort.svg. Every chapter is also on lessons/index.html.
"""

import bisect

from conftest import __


def linear_search(items, target):
    # >>> answer
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1
    # <<<


def binary_search(items, target):
    # >>> answer
    lo = 0
    hi = len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
    # <<<


def bubble_sort(items):
    # >>> answer
    result = list(items)
    n = len(result)
    for _ in range(n):
        for i in range(n - 1):
            if result[i + 1] < result[i]:
                result[i], result[i + 1] = result[i + 1], result[i]
    return result
    # <<<


def insertion_sort(items):
    # >>> answer
    result = list(items)
    for i in range(1, len(result)):
        j = i
        while j > 0 and result[j] < result[j - 1]:
            result[j], result[j - 1] = result[j - 1], result[j]
            j -= 1
    return result
    # <<<


def merge(a, b):
    merged = []
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        if b[j] < a[i]:
            merged.append(b[j])
            j += 1
        else:
            merged.append(a[i])
            i += 1
    merged.extend(a[i:])
    merged.extend(b[j:])
    return merged


def merge_sort(items):
    # >>> answer
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    return merge(left, right)
    # <<<


def partition(pivot, rest):
    less = []
    greater = []
    for item in rest:
        if item < pivot:
            less.append(item)
        else:
            greater.append(item)
    return less, greater


def quick_sort(items):
    # >>> answer
    if len(items) <= 1:
        return list(items)
    pivot = items[0]
    less, greater = partition(pivot, items[1:])
    return quick_sort(less) + [pivot] + quick_sort(greater)
    # <<<


def test_linear_search_checks_every_item_until_it_finds_one():
    """Implement linear_search above. 1. Walk the list with for index, item in enumerate(items). 2. As soon as item == target, return index. 3. If the loop finishes without returning, return -1."""
    assert linear_search([4, 8, 15, 16], 15) == 2
    assert linear_search([4, 8, 15, 16], 4) == 0
    assert linear_search([4, 8, 15, 16], 7) == -1
    assert linear_search([], 7) == -1


def test_binary_search_halves_the_sorted_list_each_step():
    """Implement binary_search above. 1. Set lo = 0 and hi = len(items) - 1, the first and last index still worth looking at. 2. While lo <= hi: set mid = (lo + hi) // 2 and look at items[mid]. If it equals target, return mid. If it is less than target, the target can only be to the right, so set lo = mid + 1. Otherwise it is greater, so set hi = mid - 1. 3. When the loop ends nothing is left to search: return -1."""
    items = [1, 3, 5, 7, 9, 11]
    assert binary_search(items, 7) == 3
    assert binary_search(items, 1) == 0
    assert binary_search(items, 11) == 5
    assert binary_search(items, 4) == -1
    assert binary_search([], 4) == -1


def test_bisect_left_is_binary_search_from_the_standard_library():
    """bisect_left returns the index of target in a sorted list, or, when target is absent, the index where it would go to keep the list sorted."""
    assert bisect.bisect_left([1, 3, 5, 7], 5) == _a(2)
    assert bisect.bisect_left([1, 3, 5, 7], 6) == _a(3)


def test_bubble_sort_swaps_neighbours_that_are_out_of_order():
    """Implement bubble_sort above. 1. Copy the input with result = list(items) so the caller's list is untouched. 2. Let n = len(result) and repeat n times: for i in range(n - 1), if result[i + 1] < result[i] swap them with result[i], result[i + 1] = result[i + 1], result[i]. Each pass carries the largest remaining item to the end, like a bubble rising. 3. Return result."""
    items = [3, 1, 2]
    assert bubble_sort(items) == [1, 2, 3]
    assert items == [3, 1, 2]
    assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    assert bubble_sort([]) == []


def test_insertion_sort_slides_each_item_left_into_place():
    """Implement insertion_sort above. 1. Copy the input with result = list(items). 2. For i in range(1, len(result)): set j = i, then while j > 0 and result[j] < result[j - 1], swap result[j] and result[j - 1] and subtract 1 from j. The item at i walks left until the item before it is not bigger, so result[:i + 1] is sorted after each i. 3. Return result."""
    items = [4, 2, 5, 1, 3]
    assert insertion_sort(items) == [1, 2, 3, 4, 5]
    assert items == [4, 2, 5, 1, 3]
    assert insertion_sort([1]) == [1]
    assert insertion_sort([]) == []


def test_merge_zips_two_sorted_lists_into_one():
    """merge is given. It keeps a finger on the front of each sorted list, always takes the smaller front item, and copies whatever is left when one list runs out."""
    assert merge([1, 4, 9], [2, 3, 10]) == _a([1, 2, 3, 4, 9, 10])
    assert merge([], [1, 2]) == _a([1, 2])


def test_merge_sort_splits_sorts_and_merges():
    """Implement merge_sort above. 1. If len(items) is 0 or 1 it is already sorted: return list(items). 2. Split at the middle: middle = len(items) // 2, then items[:middle] and items[middle:] are the halves. 3. Sort each half by calling merge_sort on it. 4. Return merge of the two sorted halves."""
    items = [5, 2, 4, 6, 1, 3]
    assert merge_sort(items) == [1, 2, 3, 4, 5, 6]
    assert items == [5, 2, 4, 6, 1, 3]
    assert merge_sort([1]) == [1]
    assert merge_sort([]) == []


def test_partition_splits_the_rest_around_a_pivot():
    """partition is given. Items smaller than the pivot go in less, everything else in greater, each keeping its arrival order."""
    assert partition(4, [7, 1, 4, 2, 9]) == _a(([1, 2], [7, 4, 9]))
    assert partition(4, []) == _a(([], []))


def test_quick_sort_sorts_around_a_pivot():
    """Implement quick_sort above. 1. If len(items) is 0 or 1 return list(items). 2. Pick pivot = items[0]. 3. Build less and greater from the rest with less, greater = partition(pivot, items[1:]). 4. Return quick_sort(less) + [pivot] + quick_sort(greater): everything smaller, sorted, then the pivot, then everything else, sorted."""
    items = [3, 6, 1, 8, 3, 2]
    assert quick_sort(items) == [1, 2, 3, 3, 6, 8]
    assert items == [3, 6, 1, 8, 3, 2]
    assert quick_sort([1]) == [1]
    assert quick_sort([]) == []


def test_key_decides_the_order_without_changing_the_items():
    """key is called once per item. sorted orders by what key returned but hands back the original items."""
    assert sorted(["bb", "a", "ccc"], key=len) == _a(["a", "bb", "ccc"])
    assert sorted([3, -5, 1], key=abs) == _a([1, 3, -5])


def test_a_stable_sort_keeps_equal_keys_in_arrival_order():
    """Two items with the same key stay in the order they came in. Sorting by suit does not disturb the order within a suit."""

    def suit(card):
        return card[0]

    cards = [("hearts", 9), ("spades", 2), ("hearts", 5)]
    assert sorted(cards, key=suit) == _a([("hearts", 9), ("hearts", 5), ("spades", 2)])


def test_lt_is_all_a_sort_needs():
    """Every comparison in this file is a < b, so a class with __lt__ from chapter 02 can be ordered by sorted and by the sorts you wrote."""

    class Card:
        def __init__(self, rank):
            self.rank = rank

        def __lt__(self, other):
            return self.rank < other.rank

    cards = [Card(9), Card(2), Card(5)]
    assert [card.rank for card in sorted(cards)] == _a([2, 5, 9])
    assert [card.rank for card in merge_sort(cards)] == _a([2, 5, 9])
    assert [card.rank for card in quick_sort(cards)] == [2, 5, 9]
