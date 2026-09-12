"""Binary trees.

A tree is nodes joined by links, like a linked list except that each node
points to up to two others, its left child and its right child. The top
node is the root. A node with no children is a leaf. None marks a missing
child, just as it marked the end of a linked list.

    class TreeNode:
        def __init__(self, value, left=None, right=None):
            self.value = value
            self.left = left
            self.right = right

Every koan below uses this one tree, built by example_tree():

            8
          /   \\
         3     10
        / \\      \\
       1   6      14

It is a binary search tree, a BST: at every node, everything in the left
subtree is smaller than the node and everything in the right subtree is
larger. To find a value, start at the root, go left if the value is
smaller, go right if it is larger, and stop when you hit it or reach None.
Each step throws away half the tree, the way binary search did.

The children of a node are themselves trees, so most tree functions are
recursive: handle None first, then do something with the node and call
yourself on each child. The height of a tree is the number of nodes on the
longest path from the root down to a leaf: 3 above, 0 for None.
"""

from collections import deque

import pytest

from conftest import __


class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def example_tree():
    return TreeNode(
        8,
        TreeNode(3, TreeNode(1), TreeNode(6)),
        TreeNode(10, None, TreeNode(14)),
    )


def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))


def size(node):
    if node is None:
        return 0
    return 1 + size(node.left) + size(node.right)


def inorder(node):
    if node is None:
        return
    yield from inorder(node.left)
    yield node.value
    yield from inorder(node.right)


def preorder(node):
    if node is None:
        return
    yield node.value
    yield from preorder(node.left)
    yield from preorder(node.right)


def postorder(node):
    if node is None:
        return
    yield from postorder(node.left)
    yield from postorder(node.right)
    yield node.value


def level_order(node):
    if node is None:
        return []
    result = []
    waiting = deque([node])
    while waiting:
        current = waiting.popleft()
        result.append(current.value)
        if current.left is not None:
            waiting.append(current.left)
        if current.right is not None:
            waiting.append(current.right)
    return result


def is_valid_bst(node, lo=None, hi=None):
    if node is None:
        return True
    if lo is not None and node.value <= lo:
        return False
    if hi is not None and node.value >= hi:
        return False
    return is_valid_bst(node.left, lo, node.value) and is_valid_bst(
        node.right, node.value, hi
    )


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        new = TreeNode(value)
        if self.root is None:
            self.root = new
            return
        node = self.root
        while True:
            if value < node.value:
                if node.left is None:
                    node.left = new
                    return
                node = node.left
            else:
                if node.right is None:
                    node.right = new
                    return
                node = node.right

    def contains(self, value):
        node = self.root
        while node is not None:
            if value == node.value:
                return True
            if value < node.value:
                node = node.left
            else:
                node = node.right
        return False

    def min_value(self):
        if self.root is None:
            raise ValueError("min of empty tree")
        node = self.root
        while node.left is not None:
            node = node.left
        return node.value

    def max_value(self):
        if self.root is None:
            raise ValueError("max of empty tree")
        node = self.root
        while node.right is not None:
            node = node.right
        return node.value

    def delete_leaf(self, value):
        parent = None
        node = self.root
        while node is not None and node.value != value:
            parent = node
            node = node.left if value < node.value else node.right
        if node is None or node.left is not None or node.right is not None:
            raise ValueError("not a leaf")
        if parent is None:
            self.root = None
        elif parent.left is node:
            parent.left = None
        else:
            parent.right = None


def example_bst():
    tree = BST()
    for value in [8, 3, 10, 1, 6, 14]:
        tree.insert(value)
    return tree


def test_a_node_has_a_value_and_two_children():
    """Read the picture in the lesson. Follow .left and .right from the root; a missing child is None."""
    root = example_tree()
    assert root.value == 8
    assert root.left.value == 3
    assert root.left.right.value == 6
    assert root.right.left is None


def test_height_counts_nodes_on_the_longest_path_down():
    """Implement height above. 1. If node is None, return 0. 2. Otherwise return 1 plus the larger of height(node.left) and height(node.right). max takes two arguments."""
    assert height(None) == 0
    assert height(TreeNode(1)) == 1
    assert height(example_tree()) == 3
    assert height(example_tree().right) == 2


def test_size_counts_every_node():
    """Implement size above. 1. If node is None, return 0. 2. Otherwise return 1 plus size(node.left) plus size(node.right)."""
    assert size(None) == 0
    assert size(TreeNode(1)) == 1
    assert size(example_tree()) == 6
    assert size(example_tree().left) == 3


def test_inorder_visits_left_then_node_then_right():
    """inorder is given. It is a generator: yield from hands over every value the left subtree yields, then the node's own value, then the right subtree's. On a BST that order is sorted."""
    assert list(inorder(example_tree())) == [1, 3, 6, 8, 10, 14]
    assert list(inorder(None)) == []


def test_preorder_visits_the_node_before_its_children():
    """Implement preorder above. 1. If node is None, return with no value, which ends the generator. 2. yield node.value. 3. yield from preorder(node.left). 4. yield from preorder(node.right). Preorder lists the root first, the order you would write the tree down to rebuild it."""
    assert list(preorder(example_tree())) == [8, 3, 1, 6, 10, 14]
    assert list(preorder(None)) == []


def test_postorder_visits_the_node_after_its_children():
    """Implement postorder above. 1. If node is None, return. 2. yield from postorder(node.left). 3. yield from postorder(node.right). 4. yield node.value. Postorder lists the root last, the order you would delete nodes so no child is left dangling."""
    assert list(postorder(example_tree())) == [1, 6, 3, 14, 10, 8]
    assert list(postorder(None)) == []


def test_insert_walks_down_and_hangs_the_new_node_on_a_none():
    """insert is given. An empty tree gets the new node as root. Otherwise walk from the root, left when the value is smaller and right when it is not, until the next step would be None, and put the new node there. Inserting 8, 3, 10, 1, 6, 14 in that order rebuilds the lesson's picture."""
    tree = BST()
    tree.insert(8)
    tree.insert(3)
    tree.insert(10)
    assert tree.root.left.value == 3
    tree.insert(6)
    assert tree.root.left.right.value == 6
    assert list(inorder(example_bst().root)) == [1, 3, 6, 8, 10, 14]


def test_contains_walks_the_same_path_insert_did():
    """Implement BST.contains above. 1. Start with node = self.root; if the tree is empty that is None. 2. While node is not None: if value equals node.value return True; if value is smaller set node = node.left, else node = node.right. 3. After the loop return False, because the walk reached a None where the value would have been."""
    tree = example_bst()
    assert tree.contains(8) is True
    assert tree.contains(6) is True
    assert tree.contains(14) is True
    assert tree.contains(7) is False
    assert BST().contains(8) is False


def test_min_value_is_as_far_left_as_you_can_go():
    """Implement BST.min_value above. 1. If self.root is None raise ValueError, as min of an empty list does. 2. Start at the root and follow .left while there is a left child. 3. Return that node's value. Nothing smaller can exist, because smaller values always go left."""
    assert example_bst().min_value() == 1
    single = BST()
    single.insert(5)
    assert single.min_value() == 5
    with pytest.raises(ValueError):
        BST().min_value()


def test_max_value_is_as_far_right_as_you_can_go():
    """Implement BST.max_value above. 1. If self.root is None raise ValueError. 2. Start at the root and follow .right while there is a right child. 3. Return that node's value."""
    assert example_bst().max_value() == 14
    single = BST()
    single.insert(5)
    assert single.max_value() == 5
    with pytest.raises(ValueError):
        BST().max_value()


def test_level_order_visits_row_by_row_using_a_queue():
    """Implement level_order above. 1. If node is None return an empty list. 2. Make an empty result list and a deque holding just node. 3. While the deque is not empty: popleft a node, append its value to result, then append its left child and its right child to the deque, skipping any that is None. 4. Return result. The queue means every node in one row is handled before the next row starts."""
    assert level_order(example_tree()) == [8, 3, 10, 1, 6, 14]
    assert level_order(TreeNode(1)) == [1]
    assert level_order(None) == []


def test_is_valid_bst_checks_every_node_against_bounds():
    """Implement is_valid_bst above. 1. If node is None return True. 2. lo and hi are the bounds every value in this subtree must stay strictly inside; None means no bound. If lo is not None and node.value <= lo return False; if hi is not None and node.value >= hi return False. 3. Return is_valid_bst(node.left, lo, node.value) and is_valid_bst(node.right, node.value, hi): going left, the node becomes the new upper bound; going right, the new lower bound. Comparing only with the parent is not enough: 6 under 10 looks fine locally but sits in 8's right subtree."""
    assert is_valid_bst(example_tree()) is True
    assert is_valid_bst(None) is True
    assert is_valid_bst(TreeNode(8, TreeNode(10), None)) is False
    sneaky = TreeNode(8, TreeNode(3), TreeNode(10, TreeNode(6), None))
    assert is_valid_bst(sneaky) is False


def test_delete_leaf_unhooks_a_node_with_no_children():
    """Implement BST.delete_leaf above. 1. Keep parent = None and node = self.root. 2. While node is not None and node.value is not value: set parent = node, then step node left if value is smaller, else right. 3. If node is None, or node has a left or a right child, raise ValueError. 4. If parent is None the leaf was the root: set self.root = None. 5. Otherwise set parent.left = None if parent.left is node, else parent.right = None."""
    tree = example_bst()
    tree.delete_leaf(6)
    assert tree.root.left.right is None
    assert list(inorder(tree.root)) == [1, 3, 8, 10, 14]
    with pytest.raises(ValueError):
        tree.delete_leaf(3)
    with pytest.raises(ValueError):
        tree.delete_leaf(99)
    single = BST()
    single.insert(1)
    single.delete_leaf(1)
    assert single.root is None


def test_a_bst_beats_a_sorted_list_when_values_keep_arriving():
    """Finding a value in a sorted list is fast, but inserting into the middle shifts everything after it. A BST inserts by walking down, so every operation costs about height steps. That only helps while the tree stays bushy: inserting already-sorted values hangs each one to the right of the last, a chain as tall as it is long."""
    bushy = BST()
    for value in [8, 3, 10, 1, 6, 14]:
        bushy.insert(value)
    chain = BST()
    for value in [1, 3, 6, 8, 10, 14]:
        chain.insert(value)
    assert height(bushy.root) == 3
    assert height(chain.root) == 6
