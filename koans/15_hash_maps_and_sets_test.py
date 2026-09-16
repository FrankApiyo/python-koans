"""Hash maps and sets.

A dict finds a value by key in one step, however many keys it holds. This
is how. It keeps a fixed number of buckets, each a small list. To store a
key it computes hash(key), an integer, and takes the remainder when divided
by the number of buckets. That remainder is the bucket index, and the pair
goes into that bucket. To find a key it computes the same index and looks
only in that one bucket.

    buckets (4 of them)
    0: [["dog", 1]]
    1: []
    2: [["cat", 2], ["emu", 3]]      two keys landed in the same bucket
    3: []

Two keys landing in the same bucket is a collision. It is normal, and it is
why a bucket is a list: the lookup walks that short list comparing keys.
As long as the buckets stay short, that walk is a few steps, so lookup is
O(1) on average. When there are more pairs than buckets, the map doubles
its bucket count and re-places every pair, which keeps buckets short.

Chapter 02 said __hash__ and __eq__ must agree. Here is why: the map finds
the bucket by hash, then finds the key inside it by ==. A key that hashes
one way and compares another is never found.

A set is the same structure storing keys with no values.

The HashMap below is built one method at a time. _bucket_for is given.
Each bucket holds [key, value] pairs as two-element lists.

Picture: lessons/svg/15_hash_buckets.svg. Every chapter is also on lessons/index.html.
"""

from collections import Counter, defaultdict

from conftest import __


class HashMap:
    def __init__(self, bucket_count=4):
        self._buckets = [[] for _ in range(bucket_count)]
        self._size = 0

    def _bucket_for(self, key):
        return self._buckets[hash(key) % len(self._buckets)]

    def set(self, key, value):
        __()

    def get(self, key, default=None):
        __()

    def __contains__(self, key):
        __()

    def __len__(self):
        return self._size

    def _resize(self):
        __()


class SameHash:
    """Every instance hashes to 1, so every one lands in the same bucket."""

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return 1

    def __eq__(self, other):
        return isinstance(other, SameHash) and self.name == other.name


def two_sum(nums, target):
    __()


def test_a_hash_is_an_integer_you_can_take_a_remainder_of():
    """hash turns any hashable value into an int. The remainder by the bucket count is always a valid index."""
    assert isinstance(hash("dog"), __)
    assert hash(42) % 4 == __


def test_bucket_for_picks_a_bucket_by_remainder():
    """_bucket_for is given. Integers hash to themselves, so 6 with four buckets lands in bucket 6 % 4."""
    hashmap = HashMap(bucket_count=4)
    assert hashmap._bucket_for(6) is hashmap._buckets[__]
    assert hashmap._bucket_for(9) is hashmap._buckets[__]


def test_set_stores_a_pair_in_its_bucket():
    """Implement HashMap.set above. 1. Get the bucket with _bucket_for(key). 2. Walk the pairs in it; if a pair's key equals key, replace that pair's value and return. 3. Otherwise append [key, value] to the bucket and add one to _size. 4. If _size is now larger than the number of buckets, call self._resize(), which a later koan implements; for now no koan crosses that line."""
    hashmap = HashMap(bucket_count=4)
    hashmap.set(6, "six")
    assert hashmap._buckets[2] == [[6, "six"]]
    hashmap.set(6, "SIX")
    assert hashmap._buckets[2] == [[6, "SIX"]]
    assert len(hashmap) == 1


def test_get_walks_one_bucket():
    """Implement HashMap.get above. 1. Walk the pairs in _bucket_for(key). 2. If a pair's key equals key return its value. 3. After the loop return default."""
    hashmap = HashMap()
    hashmap.set("dog", 1)
    hashmap.set("cat", 2)
    assert hashmap.get("dog") == 1
    assert hashmap.get("cat") == 2
    assert hashmap.get("emu") is None
    assert hashmap.get("emu", 0) == 0


def test_contains_makes_in_work():
    """Implement HashMap.__contains__ above. 1. Walk the pairs in _bucket_for(key). 2. Return True if a pair's key equals key. 3. After the loop return False."""
    hashmap = HashMap()
    hashmap.set("dog", 1)
    assert ("dog" in hashmap) is True
    assert ("cat" in hashmap) is False


def test_collisions_share_a_bucket_and_still_work():
    """Every SameHash lands in bucket 1, so the bucket holds several pairs. get still finds the right one, because it compares keys with ==."""
    hashmap = HashMap(bucket_count=4)
    hashmap.set(SameHash("a"), 1)
    hashmap.set(SameHash("b"), 2)
    assert len(hashmap._buckets[1]) == __
    assert hashmap.get(SameHash("b")) == __


def test_resize_doubles_the_buckets_and_replaces_every_pair():
    """Implement HashMap._resize above. 1. Keep the old bucket list in a local name. 2. Replace self._buckets with twice as many empty lists. 3. For every [key, value] in every old bucket, append [key, value] to _bucket_for(key), which now uses the new bucket count. Do not touch _size; nothing was added or removed."""
    hashmap = HashMap(bucket_count=2)
    for key in range(1, 4):
        hashmap.set(key, str(key))
    assert len(hashmap._buckets) == 4
    assert len(hashmap) == 3
    assert [hashmap.get(key) for key in range(1, 4)] == ["1", "2", "3"]
    assert hashmap._buckets[3] == [[3, "3"]]


def test_hash_and_eq_must_agree():
    """Chapter 02 said defining __eq__ removes __hash__. Here is the consequence: a class with __eq__ alone cannot be a key at all, because there is no way to pick a bucket."""

    class Key:
        def __init__(self, n):
            self.n = n

        def __eq__(self, other):
            return self.n == other.n

    try:
        {Key(1): "one"}
        raised = None
    except TypeError as error:
        raised = type(error)
    assert raised is __


def test_two_sum_trades_a_second_loop_for_a_dict():
    """Implement two_sum above. 1. Make an empty dict seen mapping a number to its index. 2. For each index and num in enumerate(nums): if target - num is in seen, return [seen[target - num], index]; otherwise store seen[num] = index. 3. After the loop return None. Chapter 10's slow pair loop was O(n²); this is one pass, O(n)."""
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 2, 4], 6) == [1, 2]
    assert two_sum([1, 2, 3], 100) is None


def test_counter_and_defaultdict_are_dicts_with_a_default():
    """Counter counts hashable things. defaultdict makes a missing key on first touch using the factory you give it, so no key check is needed."""
    counts = Counter("mississippi")
    assert counts["s"] == __
    groups = defaultdict(list)
    for word in ["apple", "avocado", "banana"]:
        groups[word[0]].append(word)
    assert groups["a"] == __
