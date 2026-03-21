"""
Pre-registered concept catalog.

Entries with `script_path` / `scene_class` have local Manim scripts ready to render.
Entries without them are "coming soon" and will be generated on-demand by Claude.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CatalogEntry:
    slug: str
    title: str
    description: str
    category: str
    tags: list[str]
    # Local Manim script (relative to server/) — present for pre-built entries
    script_path: Optional[str] = None
    scene_class: Optional[str] = None
    # Narration JSON (relative to server/) — pre-computed timing
    narration_path: Optional[str] = None
    duration_seconds: Optional[float] = None

    @property
    def has_script(self) -> bool:
        return self.script_path is not None


CATALOG: list[CatalogEntry] = [
    # ── Pre-built: local Manim scripts exist ──────────────────────────────────
    CatalogEntry(
        slug="recursion",
        title="Recursion",
        description="Understand recursion by tracing factorial(4) through the call stack.",
        category="concepts",
        tags=["recursion", "stack", "factorial", "fundamentals"],
        script_path="the_project/concepts/recursion.py",
        scene_class="RecursionVisualization",
        narration_path="the_project/scripts/output/recursion_narration.json",
        duration_seconds=33.4,
    ),
    CatalogEntry(
        slug="binary-search",
        title="Binary Search",
        description="See how binary search halves the search space with every comparison.",
        category="algorithms",
        tags=["binary search", "search", "sorted array", "O(log n)"],
        script_path="concepts/binary_search.py",
        scene_class="BinarySearchVisualization",
        narration_path="the_project/scripts/output/binary_search_narration.json",
        duration_seconds=18.0,
    ),
    CatalogEntry(
        slug="gradient-descent",
        title="Gradient Descent",
        description="Watch a ball roll down a loss curve — the core of machine learning optimization.",
        category="machine-learning",
        tags=["gradient descent", "optimization", "machine learning", "loss function"],
        script_path="concepts/gradient_descent.py",
        scene_class="GradientDescentVisualization",
        narration_path="the_project/scripts/output/gradient_descent_narration.json",
    ),
    CatalogEntry(
        slug="dijkstra",
        title="Dijkstra's Algorithm",
        description="Find the shortest path in a weighted graph step by step.",
        category="algorithms",
        tags=["dijkstra", "shortest path", "graph", "greedy"],
        script_path="code/explain_dijkstra.py",
        scene_class="DijkstraScene",
        narration_path="the_project/scripts/output/explain_dijkstra_narration.json",
    ),
    CatalogEntry(
        slug="factorial",
        title="Factorial Function",
        description="A visual walkthrough of how factorial builds up its result.",
        category="concepts",
        tags=["factorial", "recursion", "math", "fundamentals"],
        script_path="code/explain_factorial.py",
        scene_class="FactorialScene",
        narration_path="the_project/scripts/output/explain_factorial_narration.json",
    ),
    CatalogEntry(
        slug="tcp-handshake",
        title="TCP Three-Way Handshake",
        description="See how SYN, SYN-ACK, and ACK establish a TCP connection.",
        category="networking",
        tags=["TCP", "networking", "handshake", "protocols"],
        script_path="the_project/concepts/tcp_handshake.py",
        scene_class="TCPHandshake",
        narration_path="the_project/scripts/output/tcp_handshake_narration.json",
    ),
    # ── Coming soon: will be Claude-generated on first request ────────────────
    CatalogEntry(
        slug="bubble-sort",
        title="Bubble Sort",
        description="The simplest sorting algorithm — watch adjacent elements bubble to the top.",
        category="algorithms",
        tags=["bubble sort", "sorting", "O(n²)", "fundamentals"],
    ),
    CatalogEntry(
        slug="merge-sort",
        title="Merge Sort",
        description="Divide-and-conquer sorting: split, sort, merge.",
        category="algorithms",
        tags=["merge sort", "sorting", "divide and conquer", "O(n log n)"],
    ),
    CatalogEntry(
        slug="quick-sort",
        title="Quick Sort",
        description="Pick a pivot, partition, and recurse — one of the fastest sorting algorithms in practice.",
        category="algorithms",
        tags=["quick sort", "sorting", "pivot", "O(n log n)"],
    ),
    CatalogEntry(
        slug="bfs",
        title="Breadth-First Search",
        description="Explore a graph level by level using a queue.",
        category="algorithms",
        tags=["BFS", "graph traversal", "queue", "shortest path"],
    ),
    CatalogEntry(
        slug="dfs",
        title="Depth-First Search",
        description="Explore a graph by going as deep as possible before backtracking.",
        category="algorithms",
        tags=["DFS", "graph traversal", "stack", "backtracking"],
    ),
    CatalogEntry(
        slug="dynamic-programming",
        title="Dynamic Programming",
        description="Solve Fibonacci with memoization — stop recomputing the same subproblems.",
        category="algorithms",
        tags=["dynamic programming", "memoization", "fibonacci", "optimization"],
    ),
    CatalogEntry(
        slug="hash-map",
        title="Hash Maps",
        description="How a hash function maps keys to buckets — and what happens on collisions.",
        category="data-structures",
        tags=["hash map", "hash table", "O(1)", "collisions"],
    ),
    CatalogEntry(
        slug="linked-list",
        title="Linked Lists",
        description="Nodes pointing to nodes — how insertion and deletion work in a linked list.",
        category="data-structures",
        tags=["linked list", "pointers", "nodes", "data structures"],
    ),
    CatalogEntry(
        slug="binary-tree",
        title="Binary Trees",
        description="Insert, search, and traverse a binary search tree visually.",
        category="data-structures",
        tags=["binary tree", "BST", "traversal", "data structures"],
    ),
    CatalogEntry(
        slug="heap",
        title="Heaps & Priority Queues",
        description="How a max-heap stays sorted after every insert and extract.",
        category="data-structures",
        tags=["heap", "priority queue", "O(log n)", "data structures"],
    ),
]

# Lookup by slug
CATALOG_BY_SLUG: dict[str, CatalogEntry] = {e.slug: e for e in CATALOG}
