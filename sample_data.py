"""
sample_data.py - High-quality demonstration questions for QuizMaster AI.

Works 100% offline without requiring any API keys.
Covers core Computer Science concepts across various difficulties and topics.
"""

from typing import List, Dict, Any
from quiz_logic import Question, validate_and_deduplicate_questions

SAMPLE_QUESTIONS_RAW: List[Dict[str, Any]] = [
    {
        "id": "cs_01",
        "prompt": "What is the worst-case time complexity of searching for an element in an unsorted array of n elements?",
        "options": {
            "A": "O(1)",
            "B": "O(log n)",
            "C": "O(n)",
            "D": "O(n²)"
        },
        "correct_option": "C",
        "explanation": "In an unsorted array, the target element may be located at the very end or not present at all. Therefore, a linear search must inspect every element one by one, resulting in O(n) worst-case time complexity.",
        "topic": "Algorithms",
        "difficulty": "Easy",
        "source_reference": "Lecture Notes: Introduction to Asymptotic Analysis & Linear Search."
    },
    {
        "id": "cs_02",
        "prompt": "Which data structure follows the Last-In, First-Out (LIFO) principle?",
        "options": {
            "A": "Queue",
            "B": "Stack",
            "C": "Linked List",
            "D": "Binary Search Tree"
        },
        "correct_option": "B",
        "explanation": "A Stack operates on the LIFO principle, where the most recently added item is the first one removed (e.g., call stack or undo functionality). Queues follow FIFO (First-In, First-Out).",
        "topic": "Data Structures",
        "difficulty": "Easy",
        "source_reference": "Lecture Notes: Abstract Data Types - Stacks vs Queues."
    },
    {
        "id": "cs_03",
        "prompt": "In Python, which of the following data types is immutable?",
        "options": {
            "A": "List",
            "B": "Dictionary",
            "C": "Set",
            "D": "Tuple"
        },
        "correct_option": "D",
        "explanation": "Tuples are immutable in Python; once created, their elements cannot be modified, added, or removed. Lists, Dictionaries, and Sets are all mutable.",
        "topic": "Python Basics",
        "difficulty": "Easy",
        "source_reference": "Lecture Notes: Python Memory Model and Primitive Types."
    },
    {
        "id": "cs_04",
        "prompt": "What happens when a recursive function lacks a valid base case?",
        "options": {
            "A": "The function executes in O(1) time.",
            "B": "A stack overflow occurs due to unbounded call stack frames.",
            "C": "The compiler automatically injects an exit condition.",
            "D": "The function returns None immediately."
        },
        "correct_option": "B",
        "explanation": "Without a terminating base case, each recursive call adds a new stack frame to memory until the call stack limit is exceeded, triggering a stack overflow error (or RecursionError in Python).",
        "topic": "Algorithms",
        "difficulty": "Medium",
        "source_reference": "Lecture Notes: Recursion & Stack Frames."
    },
    {
        "id": "cs_05",
        "prompt": "What is the average-case time complexity of lookup in a properly balanced Hash Table?",
        "options": {
            "A": "O(1)",
            "B": "O(log n)",
            "C": "O(n)",
            "D": "O(n log n)"
        },
        "correct_option": "A",
        "explanation": "Hash tables compute an index via a hash function, allowing direct memory addressing in O(1) expected time on average when collisions are well distributed.",
        "topic": "Data Structures",
        "difficulty": "Medium",
        "source_reference": "Lecture Notes: Hash Maps & Collision Resolution."
    },
    {
        "id": "cs_06",
        "prompt": "What is the primary difference between a process and a thread in modern operating systems?",
        "options": {
            "A": "Processes share address space; threads have independent memory spaces.",
            "B": "Threads have separate process identifiers and isolated memory spaces.",
            "C": "Processes have isolated memory spaces; threads within a process share the same address space.",
            "D": "Threads cannot run concurrently on multi-core processors."
        },
        "correct_option": "C",
        "explanation": "Processes are isolated execution environments with dedicated address spaces. Threads exist within a process and share its heap, global variables, and open files, while retaining their own register sets and stacks.",
        "topic": "Computer Systems",
        "difficulty": "Medium",
        "source_reference": "Lecture Notes: Operating Systems - Concurrency & Processes."
    },
    {
        "id": "cs_07",
        "prompt": "In HTTP semantics, which HTTP method is specified to be idempotent and used to retrieve representation of a resource without side effects?",
        "options": {
            "A": "POST",
            "B": "GET",
            "C": "PATCH",
            "D": "CONNECT"
        },
        "correct_option": "B",
        "explanation": "GET is safe and idempotent; making multiple identical GET requests has no modifying side effects on the server state compared to a single request.",
        "topic": "Web Fundamentals",
        "difficulty": "Easy",
        "source_reference": "Lecture Notes: Web Architecture & HTTP Methods."
    },
    {
        "id": "cs_08",
        "prompt": "Which sorting algorithm guarantees O(n log n) worst-case time complexity regardless of initial input order?",
        "options": {
            "A": "Quick Sort",
            "B": "Bubble Sort",
            "C": "Merge Sort",
            "D": "Insertion Sort"
        },
        "correct_option": "C",
        "explanation": "Merge Sort always divides the array evenly into halves (log n levels) and merges in linear time O(n), guaranteeing O(n log n) worst-case time. Standard Quick Sort degrades to O(n²) when pivot selection is poor.",
        "topic": "Algorithms",
        "difficulty": "Medium",
        "source_reference": "Lecture Notes: Divide & Conquer Sorting."
    },
    {
        "id": "cs_09",
        "prompt": "In object-oriented programming, what principle states that derived classes must be substitutable for their base classes without altering program correctness?",
        "options": {
            "A": "Single Responsibility Principle",
            "B": "Liskov Substitution Principle",
            "C": "Interface Segregation Principle",
            "D": "Open/Closed Principle"
        },
        "correct_option": "B",
        "explanation": "The Liskov Substitution Principle (the 'L' in SOLID) requires that subtypes preserve the behavior and contracts expected of their base types without throwing unexpected exceptions or violating post-conditions.",
        "topic": "Software Design",
        "difficulty": "Hard",
        "source_reference": "Lecture Notes: SOLID Design Principles."
    },
    {
        "id": "cs_10",
        "prompt": "What is the primary role of a database index implemented as a B-Tree?",
        "options": {
            "A": "Compressing database records to save disk space.",
            "B": "Accelerating data retrieval by minimizing disk I/O operations through logarithmic height.",
            "C": "Encrypting sensitive columns stored on disk.",
            "D": "Enforcing foreign key constraints across tables."
        },
        "correct_option": "B",
        "explanation": "B-Trees are self-balancing search trees with high branching factors (fan-out) optimized for block storage, enabling fast record lookups with minimal disk page reads.",
        "topic": "Data Structures",
        "difficulty": "Hard",
        "source_reference": "Lecture Notes: Database Systems & Secondary Storage Indexing."
    },
    {
        "id": "cs_11",
        "prompt": "In Python, what is the behavior of the `global interpreter lock` (GIL) in standard CPython?",
        "options": {
            "A": "It prevents memory leaks by automatically deleting unreferenced objects.",
            "B": "It enforces that only one native thread executes Python bytecode at any given moment.",
            "C": "It locks file I/O operations so only one process can write to disk.",
            "D": "It prevents recursive functions from exceeding 1000 frames."
        },
        "correct_option": "B",
        "explanation": "The CPython GIL is a mutex that prevents multiple native threads from executing Python bytecode concurrently, primarily to protect CPython's reference-counting memory management.",
        "topic": "Python Basics",
        "difficulty": "Hard",
        "source_reference": "Lecture Notes: CPython Internals & Threading."
    },
    {
        "id": "cs_12",
        "prompt": "Which network layer in the OSI model is responsible for reliable end-to-end data transmission, flow control, and error recovery (e.g., TCP)?",
        "options": {
            "A": "Network Layer (Layer 3)",
            "B": "Data Link Layer (Layer 2)",
            "C": "Transport Layer (Layer 4)",
            "D": "Session Layer (Layer 5)"
        },
        "correct_option": "C",
        "explanation": "The Transport Layer (Layer 4) provides transparent transfer of data between end systems, providing services such as connection-oriented communication, reliability, flow control, and multiplexing.",
        "topic": "Computer Systems",
        "difficulty": "Easy",
        "source_reference": "Lecture Notes: Computer Networks - OSI 7-Layer Model."
    },
    {
        "id": "cs_13",
        "prompt": "What is the space complexity of Depth-First Search (DFS) on a tree of maximum depth d with branching factor b?",
        "options": {
            "A": "O(b^d)",
            "B": "O(d)",
            "C": "O(b * d)",
            "D": "O(log d)"
        },
        "correct_option": "B",
        "explanation": "DFS only needs to store the current path of nodes from the root down to the leaf on its call stack, resulting in space complexity proportional to the maximum tree depth, O(d).",
        "topic": "Algorithms",
        "difficulty": "Hard",
        "source_reference": "Lecture Notes: Graph Traversal & Search Algorithms."
    },
    {
        "id": "cs_14",
        "prompt": "In Python, which built-in function returns an iterator of tuples containing index counts and corresponding values from an iterable?",
        "options": {
            "A": "zip()",
            "B": "range()",
            "C": "map()",
            "D": "enumerate()"
        },
        "correct_option": "D",
        "explanation": "`enumerate(iterable)` returns an enumerate object yielding tuples of `(index, value)`, useful for loops requiring index tracking without manual counter increments.",
        "topic": "Python Basics",
        "difficulty": "Easy",
        "source_reference": "Lecture Notes: Python Iterators & Built-ins."
    },
    {
        "id": "cs_15",
        "prompt": "What condition must be satisfied to prevent deadlock according to the Coffman conditions?",
        "options": {
            "A": "At least one of Mutual Exclusion, Hold & Wait, No Preemption, or Circular Wait must be eliminated.",
            "B": "All threads must share the same priority level.",
            "C": "CPU utilization must remain below 80%.",
            "D": "All locks must be re-entrant.",
        },
        "correct_option": "A",
        "explanation": "Deadlock can only occur if all four Coffman conditions hold simultaneously. Eliminating even one condition (such as breaking Circular Wait through resource ordering) prevents deadlock entirely.",
        "topic": "Computer Systems",
        "difficulty": "Hard",
        "source_reference": "Lecture Notes: Operating Systems - Deadlock Prevention."
    }
]


def get_sample_quiz(count: int = 5, difficulty: str = "Medium") -> List[Question]:
    """
    Returns a validated list of sample questions matching requested count and difficulty.
    If filtered difficulty has fewer questions than count, gracefully fills from other difficulties.
    """
    valid_all = validate_and_deduplicate_questions(SAMPLE_QUESTIONS_RAW)
    if not valid_all:
        return []

    # Map raw difficulty for filtering
    diff_map = {item["id"]: item.get("difficulty", "Medium") for item in SAMPLE_QUESTIONS_RAW}

    target_diff = difficulty.capitalize()
    matching = [q for q in valid_all if diff_map.get(q.id) == target_diff]
    others = [q for q in valid_all if diff_map.get(q.id) != target_diff]

    combined = matching + others
    requested_count = min(count, len(combined))
    return combined[:requested_count]


SAMPLE_LECTURE_NOTES = """Lecture 4: Fundamentals of Data Structures and Algorithm Analysis

1. Asymptotic Notation:
Time complexity describes how execution time grows with input size n.
- O(1): Constant time, e.g., accessing an array element by index.
- O(log n): Logarithmic time, e.g., binary search on sorted data.
- O(n): Linear time, e.g., finding an item in an unsorted array or linked list.
- O(n log n): Efficient sorting, e.g., Merge Sort and Quick Sort average case.
- O(n²): Quadratic time, e.g., nested loops in Bubble Sort.

2. Stacks vs. Queues:
- Stack: Follows Last-In, First-Out (LIFO). Standard operations are push (insert), pop (remove top), and peek. Stacks are essential for managing function call frames, recursion, and undo history in editors.
- Queue: Follows First-In, First-Out (FIFO). Standard operations are enqueue (insert at rear) and dequeue (remove from front). Used for printer queues and breadth-first search.

3. Hash Tables:
A hash table maps keys to values using a hash function. In an optimal scenario with minimal collisions, lookup, insertion, and deletion operate in expected O(1) average time. When collisions occur, techniques like chaining (linked lists) or open addressing (probing) are used to resolve them.
"""
