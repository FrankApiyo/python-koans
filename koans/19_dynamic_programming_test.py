"""Dynamic programming.

Some problems break into smaller copies of themselves, and the same small
copies come up again and again. Chapter 13's naive fib is the classic case:
fib(5) asks for fib(4) and fib(3), fib(4) asks for fib(3) again, and so on
until fib(2) has been computed hundreds of times. That repetition is called
overlapping subproblems, and dynamic programming is the habit of solving
each subproblem once.

Two ways to do it.

Memoisation is top down: write the recursive function, but keep a dict of
answers already found and return from it before recursing.

    def fib(n, memo):
        if n < 2:
            return n
        if n not in memo:
            memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
        return memo[n]

Tabulation is bottom up: make a table, fill in the smallest cases by hand,
then fill each next cell from cells already filled, with no recursion.

    table = [0, 1]
    for i in range(2, n + 1):
        table.append(table[i - 1] + table[i - 2])

Both turn exponential work into linear. The chapter ends with two problems
whose tables are less obvious than fib's, so you can see the pattern: name
the subproblem, decide how a cell depends on earlier cells, fill in order.

Picture: lessons/svg/19_fib_overlap.svg and 19_lcs_grid.svg. Every chapter is also on lessons/index.html.
"""

from conftest import __

calls = {"count": 0}


def fib_naive(n):
    calls["count"] += 1
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n, memo=None):
    __()


def fib_table(n):
    __()


def climb_stairs(n):
    __()


def min_coins(coins, amount):
    __()


def lcs(a, b):
    __()


def test_naive_fib_repeats_the_same_small_calls():
    """fib_naive is given and counts its calls. fib(20) is only twenty numbers long, yet the calls run into the thousands, because each subproblem is recomputed from scratch."""
    calls["count"] = 0
    assert fib_naive(20) == __
    assert calls["count"] == __


def test_memoisation_solves_each_subproblem_once():
    """Implement fib_memo above. 1. If memo is None, make it an empty dict. 2. If n is less than 2 return n. 3. If n is not in memo, store fib_memo(n - 1, memo) + fib_memo(n - 2, memo) under memo[n]. 4. Return memo[n]. Each n is computed once, so fib(80) is instant."""
    assert fib_memo(20) == 6765
    assert fib_memo(80) == 23416728348467685


def test_tabulation_fills_a_table_from_the_bottom():
    """Implement fib_table above. 1. Start table = [0, 1]. 2. For i from 2 to n inclusive, append table[i - 1] + table[i - 2]. 3. Return table[n]. No recursion, so no recursion limit either."""
    assert fib_table(0) == 0
    assert fib_table(1) == 1
    assert fib_table(20) == 6765
    assert fib_table(500) == fib_memo(500)


def test_climbing_stairs_is_fib_in_disguise():
    """Implement climb_stairs above. You can climb one or two steps at a time; how many distinct ways reach step n? 1. ways = [1, 1], since there is one way to stand on step 0 and one way to reach step 1. 2. For i from 2 to n inclusive, the ways to reach step i are ways[i - 1] plus ways[i - 2], because the last move was a single or a double step. 3. Return ways[n]."""
    assert climb_stairs(2) == 2
    assert climb_stairs(3) == 3
    assert climb_stairs(10) == 89


def test_min_coins_tries_every_coin_for_every_amount():
    """Implement min_coins above. 1. Make table of size amount + 1 filled with float("inf"), and set table[0] = 0: zero coins make zero. 2. For each current amount from 1 to amount, for each coin no larger than current, if table[current - coin] + 1 is smaller than table[current], store it. 3. If table[amount] is still inf return -1, else return it. The subproblem is "fewest coins for a smaller amount", and each cell looks back one coin."""
    assert min_coins([1, 5, 10], 18) == 5
    assert min_coins([2], 3) == -1
    assert min_coins([1, 3, 4], 6) == 2
    assert min_coins([1], 0) == 0


def test_longest_common_subsequence_fills_a_grid():
    """Implement lcs above. 1. Make table with len(a) + 1 rows and len(b) + 1 columns of zeros; row 0 and column 0 stay zero, meaning an empty prefix shares nothing. 2. For i from 1 to len(a) and j from 1 to len(b): if a[i - 1] equals b[j - 1], table[i][j] is the diagonal cell table[i - 1][j - 1] plus 1; otherwise it is the larger of the cell above, table[i - 1][j], and the cell to the left, table[i][j - 1]. 3. Return the bottom-right cell. Each cell answers "longest shared subsequence of these two prefixes"."""
    assert lcs("abcde", "ace") == 3
    assert lcs("abc", "abc") == 3
    assert lcs("abc", "def") == 0
    assert lcs("", "abc") == 0


def test_when_dynamic_programming_applies():
    """Two signs. Overlapping subproblems: the same smaller question is asked many times. Optimal substructure: the best answer is built from best answers to smaller cases. fib has both; a plain list search has neither."""
    signs = {
        "the same smaller question is asked many times": "overlapping subproblems",
        "the best answer is built from best smaller answers": "optimal substructure",
    }
    assert signs["the same smaller question is asked many times"] == __
    assert signs["the best answer is built from best smaller answers"] == __


def test_enlightenment():
    """You began with a class and self. You end with a grid of subproblems. Every structure between was a class with a list or a few pointers and one method at a time. Run git checkout -- koans/ and go again; the second pass is where it sticks."""
    assert "Enlightenment".lower() == __
