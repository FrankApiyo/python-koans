"""Graphs.

A graph is a set of nodes joined by edges. A road map is a graph: towns are
nodes, roads are edges. A tree is a graph with no cycles and one root; a
graph in general can loop back on itself and has no root, so every walk
must remember where it has been.

The simplest way to store one is an adjacency dict: each node maps to the
list of nodes it is joined to. The example graph every koan here uses:

    A --- B --- D
    |     |
    C --- E     F      (F is on its own)

    {"A": ["B", "C"], "B": ["A", "D", "E"], "C": ["A", "E"],
     "D": ["B"], "E": ["B", "C"], "F": []}

Two ways to walk it. Breadth-first search (BFS) visits everything one step
from the start, then everything two steps away, and so on, using a queue.
Depth-first search (DFS) follows one path as far as it goes before backing
up, using recursion or a stack. Both keep a set of seen nodes so a cycle
cannot trap them. Neighbours are visited in the order they were added, so
every visit order below can be read off the picture.

A directed graph has one-way edges: add_edge with directed=True joins a to b
only. A weighted graph puts a number on each edge, and finding the cheapest
route is Dijkstra's algorithm, which is BFS with a heap in place of the
queue. Chapters 11, 13 and 17 gave you the deque, recursion, and heapq.

Picture: lessons/svg/18_bfs_dfs.svg and 18_dijkstra.svg. Every chapter is also on lessons/index.html.
"""

import heapq
from collections import deque

from conftest import __


class Graph:
    def __init__(self):
        self._adj = {}

    def add_node(self, node):
        self._adj.setdefault(node, [])

    def add_edge(self, a, b, directed=False):
        self.add_node(a)
        self.add_node(b)
        self._adj[a].append(b)
        if not directed:
            self._adj[b].append(a)

    def neighbours(self, node):
        return self._adj[node]

    def nodes(self):
        return list(self._adj)

    def bfs(self, start):
        order = []
        seen = {start}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbour in self.neighbours(node):
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        return order

    def dfs(self, start):
        order = []
        seen = set()

        def visit(node):
            seen.add(node)
            order.append(node)
            for neighbour in self.neighbours(node):
                if neighbour not in seen:
                    visit(neighbour)

        visit(start)
        return order

    def dfs_iterative(self, start):
        order = []
        seen = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            order.append(node)
            for neighbour in reversed(self.neighbours(node)):
                if neighbour not in seen:
                    stack.append(neighbour)
        return order

    def has_path(self, a, b):
        return b in self.bfs(a)

    def shortest_path(self, a, b):
        parent = {a: None}
        queue = deque([a])
        while queue:
            node = queue.popleft()
            if node == b:
                break
            for neighbour in self.neighbours(node):
                if neighbour not in parent:
                    parent[neighbour] = node
                    queue.append(neighbour)
        if b not in parent:
            return None
        path = []
        node = b
        while node is not None:
            path.append(node)
            node = parent[node]
        return list(reversed(path))

    def has_cycle(self):
        seen = set()

        def visit(node, parent):
            seen.add(node)
            for neighbour in self.neighbours(node):
                if neighbour not in seen:
                    if visit(neighbour, node):
                        return True
                elif neighbour != parent:
                    return True
            return False

        return any(node not in seen and visit(node, None) for node in self.nodes())

    def topological_sort(self):
        in_degree = {node: 0 for node in self.nodes()}
        for node in self.nodes():
            for neighbour in self.neighbours(node):
                in_degree[neighbour] += 1
        queue = deque(node for node in self.nodes() if in_degree[node] == 0)
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbour in self.neighbours(node):
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    queue.append(neighbour)
        return order


class WeightedGraph:
    def __init__(self):
        self._adj = {}

    def add_edge(self, a, b, weight):
        self._adj.setdefault(a, []).append((b, weight))
        self._adj.setdefault(b, []).append((a, weight))

    def dijkstra(self, start):
        dist = {node: float("inf") for node in self._adj}
        dist[start] = 0
        heap = [(0, start)]
        while heap:
            distance, node = heapq.heappop(heap)
            if distance > dist[node]:
                continue
            for neighbour, weight in self._adj[node]:
                candidate = distance + weight
                if candidate < dist[neighbour]:
                    dist[neighbour] = candidate
                    heapq.heappush(heap, (candidate, neighbour))
        return dist


def example():
    graph = Graph()
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "D")
    graph.add_edge("B", "E")
    graph.add_edge("C", "E")
    graph.add_node("F")
    return graph


def tasks():
    """A directed graph of chores: an edge a -> b means a must happen before b."""
    graph = Graph()
    graph.add_edge("wake", "shower", directed=True)
    graph.add_edge("wake", "coffee", directed=True)
    graph.add_edge("shower", "dress", directed=True)
    graph.add_edge("coffee", "leave", directed=True)
    graph.add_edge("dress", "leave", directed=True)
    return graph


def test_an_adjacency_dict_lists_each_nodes_neighbours():
    """add_edge is given. Undirected means both nodes list each other. F was added with no edges, so its list is empty."""
    graph = example()
    assert graph.neighbours("B") == ["A", "D", "E"]
    assert graph.neighbours("F") == []


def test_a_directed_edge_goes_one_way():
    """With directed=True only a lists b. b does not know about a."""
    graph = tasks()
    assert graph.neighbours("wake") == ["shower", "coffee"]
    assert graph.neighbours("shower") == ["dress"]


def test_bfs_visits_by_distance():
    """Implement Graph.bfs above. 1. Make an empty order list, a seen set holding start, and a deque holding start. 2. While the deque is not empty: popleft a node, append it to order, and for each neighbour not in seen, add it to seen and append it to the deque. 3. Return order. Everything one step from A comes before anything two steps away."""
    assert example().bfs("A") == ["A", "B", "C", "D", "E"]
    assert example().bfs("D") == ["D", "B", "A", "E", "C"]
    assert example().bfs("F") == ["F"]


def test_dfs_follows_one_path_to_the_end_first():
    """Implement Graph.dfs above. 1. Make an empty order list and an empty seen set. 2. Define an inner function visit(node) that adds node to seen, appends it to order, and calls visit on each neighbour not in seen. 3. Call visit(start) and return order. From A it dives A, B, D, then backs up to B's next neighbour E, then E's neighbour C."""
    assert example().dfs("A") == ["A", "B", "D", "E", "C"]
    assert example().dfs("F") == ["F"]


def test_dfs_with_a_stack_instead_of_recursion():
    """Implement Graph.dfs_iterative above. 1. Make an empty order list, an empty seen set, and a stack list holding start. 2. While the stack is not empty: pop a node; if it is in seen, continue; add it to seen and append it to order; then push each neighbour not in seen, in reversed order so the first neighbour is popped first. 3. Return order. The visit order matches the recursive version."""
    assert example().dfs_iterative("A") == ["A", "B", "D", "E", "C"]
    assert example().dfs_iterative("F") == ["F"]


def test_has_path_asks_whether_a_walk_reaches_the_target():
    """Implement Graph.has_path above. 1. Return whether b is in self.bfs(a). Any walk that visits everything reachable will do."""
    graph = example()
    assert graph.has_path("A", "D") is True
    assert graph.has_path("A", "F") is False
    assert graph.has_path("F", "F") is True


def test_shortest_path_records_where_each_node_was_reached_from():
    """Implement Graph.shortest_path above. 1. Make a parent dict {a: None} and a deque holding a. 2. Run BFS: popleft a node; if it is b, break; for each neighbour not in parent, set parent[neighbour] = node and append it. 3. If b is not in parent, return None. 4. Walk back from b through parent until None, collecting nodes into a list, and return that list reversed. BFS reaches each node first by a shortest route, so the parent chain is a shortest path."""
    graph = example()
    assert graph.shortest_path("A", "E") == ["A", "B", "E"]
    assert graph.shortest_path("D", "C") == ["D", "B", "A", "C"]
    assert graph.shortest_path("A", "A") == ["A"]
    assert graph.shortest_path("A", "F") is None


def test_has_cycle_spots_a_neighbour_seen_before_that_is_not_the_parent():
    """Implement Graph.has_cycle above. 1. Make an empty seen set. 2. Define visit(node, parent): add node to seen; for each neighbour, if it is not seen, return True if visit(neighbour, node) does; else if it is not parent, return True, because reaching a seen node by a new edge closes a loop. Return False at the end. 3. Return whether visit(node, None) is True for any node not yet seen, so nodes cut off from the start are checked too."""
    assert example().has_cycle() is True
    line = Graph()
    line.add_edge("A", "B")
    line.add_edge("B", "C")
    assert line.has_cycle() is False


def test_topological_sort_orders_a_directed_graph_by_dependencies():
    """Implement Graph.topological_sort above. 1. Make in_degree, a dict of every node to 0, then add 1 to in_degree[neighbour] for every edge. 2. Make a deque of every node whose in_degree is 0. 3. While the deque is not empty: popleft a node, append it to order, and for each neighbour subtract 1 from its in_degree; when that reaches 0, append the neighbour to the deque. 4. Return order. Every task comes after everything it depends on."""
    order = tasks().topological_sort()
    assert order.index("wake") < order.index("shower")
    assert order.index("shower") < order.index("dress")
    assert order.index("dress") < order.index("leave")
    assert order.index("coffee") < order.index("leave")
    assert len(order) == 5


def test_a_weighted_edge_carries_a_number():
    """WeightedGraph.add_edge is given. Each neighbour is stored as a (node, weight) pair."""
    graph = WeightedGraph()
    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 1)
    assert graph._adj["A"] == [("B", 4), ("C", 1)]


def test_dijkstra_finds_the_cheapest_route_to_every_node():
    """Implement WeightedGraph.dijkstra above. 1. Make dist, a dict of every node to float("inf"), and set dist[start] = 0. 2. Make a heap list holding (0, start). 3. While the heap is not empty: heappop the smallest (distance, node); if distance is greater than dist[node] this entry is stale, so continue; for each (neighbour, weight) of node, compute candidate = distance + weight and, if it beats dist[neighbour], store it and heappush (candidate, neighbour). 4. Return dist."""
    graph = WeightedGraph()
    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 1)
    graph.add_edge("C", "B", 2)
    graph.add_edge("B", "D", 5)
    assert graph.dijkstra("A") == {"A": 0, "B": 3, "C": 1, "D": 8}


def test_an_unreachable_node_stays_at_infinity():
    """dist starts every node at inf and only lowers what the walk can reach. A node with no route keeps inf."""
    graph = WeightedGraph()
    graph.add_edge("A", "B", 1)
    graph.add_edge("C", "D", 1)
    assert graph.dijkstra("A")["D"] == float("inf")


def test_bfs_or_dfs():
    """BFS finds shortest paths in unweighted graphs and needs a queue. DFS is simpler to write recursively and suits cycle detection and exhaustive exploration."""
    choice = {
        "fewest hops between two towns": "bfs",
        "does this dependency graph loop": "dfs",
    }
    assert choice["fewest hops between two towns"] == "bfs"
    assert choice["does this dependency graph loop"] == "dfs"
