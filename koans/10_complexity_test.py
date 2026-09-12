"""Complexity.

Before building any structure, you need a way to say how much work an
operation does as the input grows. Seconds are a bad measure: they change
with the machine. Instead, count steps, and look at the shape of the count
as the input size n grows. That shape is what Big-O names.

    O(1)      constant     the same steps however big n is
    O(log n)  logarithmic  steps grow by one each time n doubles
    O(n)      linear       steps grow in step with n
    O(n²)     quadratic    steps grow with n times n

A list index, items[3], is O(1): it goes straight to the slot. Searching a
list with "in" is O(n): it may compare against every element. A loop inside
a loop over the same list is O(n²). A set stores each item in a slot chosen
by its hash, so "in" on a set is O(1) on average, however large the set.

The wrapper below counts every comparison and every index a list makes, so
you can see these shapes as numbers rather than take them on trust.

    counted = Counted([10, 20, 30])
    30 in counted        # compares 10, 20, 30: three steps
    counted.steps        # 3
"""

from conftest import __


class Counted:
    """A list that counts how many elements it looks at."""

    def __init__(self, items):
        self._items = list(items)
        self.steps = 0

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        self.steps += 1
        return self._items[index]

    def __contains__(self, value):
        for item in self._items:
            self.steps += 1
            if item == value:
                return True
        return False


class CountedSet:
    """A set that counts how many hash lookups it makes."""

    def __init__(self, items):
        self._items = set(items)
        self.steps = 0

    def __contains__(self, value):
        self.steps += 1
        return value in self._items


def has_duplicate_slow(counted):
    __()


def has_duplicate_fast(counted):
    __()


def test_indexing_is_one_step_however_long_the_list():
    """items[i] goes straight to slot i. It does not matter whether the list has ten elements or ten million."""
    short = Counted(range(10))
    long = Counted(range(10_000))
    short[7]
    long[7_000]
    assert short.steps == __
    assert long.steps == __


def test_in_on_a_list_walks_until_it_finds_the_value():
    """Searching starts at index 0 and compares each element in turn. The last element costs as many steps as the list is long."""
    counted = Counted([10, 20, 30, 40])
    assert (40 in counted) is True
    assert counted.steps == __


def test_in_on_a_list_walks_the_whole_list_when_the_value_is_missing():
    """A miss is the worst case: every element is compared. Big-O describes this worst case, so list membership is O(n)."""
    counted = Counted(range(1000))
    assert (-1 in counted) is False
    assert counted.steps == __


def test_in_on_a_set_is_one_step():
    """A set hashes the value and looks in one slot. Hit or miss, large or small, it is one lookup: O(1)."""
    small = CountedSet(range(10))
    large = CountedSet(range(10_000))
    assert (-1 in small) is False
    assert (9_999 in large) is True
    assert small.steps == __
    assert large.steps == __


def test_a_loop_inside_a_loop_is_quadratic():
    """Implement has_duplicate_slow above. 1. For each index i in range(len(counted)), for each index j from i + 1 to the end, compare counted[i] with counted[j]; if they are equal return True. 2. After both loops return False. With n distinct elements every pair is looked at, so the step count grows like n * n."""
    ten = Counted(range(10))
    assert has_duplicate_slow(ten) is False
    assert ten.steps == 90
    twenty = Counted(range(20))
    assert has_duplicate_slow(twenty) is False
    assert twenty.steps == 380


def test_a_set_makes_the_same_question_linear():
    """Implement has_duplicate_fast above. 1. Make an empty set called seen. 2. For each index i in range(len(counted)): if counted[i] is in seen return True, otherwise add counted[i] to seen. 3. After the loop return False. Each element is indexed twice at most, so the count grows like n, not n * n."""
    ten = Counted(range(10))
    assert has_duplicate_fast(ten) is False
    assert ten.steps == 20
    twenty = Counted(range(20))
    assert has_duplicate_fast(twenty) is False
    assert twenty.steps == 40
    assert has_duplicate_fast(Counted([1, 2, 1])) is True


def test_the_shape_matters_more_than_the_constant():
    """Doubling n doubles a linear count and quadruples a quadratic one. 2n and n look the same in Big-O; n and n * n do not."""
    linear = {n: 2 * n for n in (10, 20, 40)}
    quadratic = {n: n * n for n in (10, 20, 40)}
    assert linear[40] // linear[20] == __
    assert quadratic[40] // quadratic[20] == __


def test_name_the_shape():
    """Match each operation to its Big-O. The three shapes here are the ones the rest of these koans keep returning to."""
    shapes = {
        "index into a list": "O(1)",
        "search a list with in": "O(n)",
        "compare every pair in a list": "O(n²)",
        "search a set with in": "O(1)",
    }
    assert shapes["search a list with in"] == __
    assert shapes["search a set with in"] == __
