import sys
import os

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import get_db, init_db

def seed_database():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # 1. Insert Subject
    cursor.execute("SELECT id FROM subjects WHERE code = 'PYTHON'")
    existing_subject = cursor.fetchone()
    if existing_subject:
        print("[SEED] Subject already seeded.")
        subject_id = existing_subject["id"]
    else:
        cursor.execute("""
            INSERT INTO subjects (name, code, description, icon)
            VALUES (?, ?, ?, ?)
        """, (
            "Python Programming",
            "PYTHON",
            "Master Python fundamentals, control structures, functions, and data structures through adaptive micro-learning.",
            "fa-brands fa-python"
        ))
        subject_id = cursor.lastrowid
        print(f"[SEED] Created Python subject with ID: {subject_id}")

    # 2. Insert Topics
    topics_data = [
        (1, "Python Syntax & Variables", "Variables, primitive data types, type casting, and standard I/O operations."),
        (2, "Control Flow & Decision Making", "Conditional statements (if, elif, else), logical and comparison operators."),
        (3, "Loops & Iterations", "Iteration patterns using for loops, while loops, range(), break, and continue."),
        (4, "Functions & Scope", "Defining functions, parameters, return values, docstrings, and variable scope."),
        (5, "Data Structures (Lists & Dictionaries)", "Sequential data processing with lists, tuples, and key-value mapping dictionaries.")
    ]

    topic_id_map = {}
    for seq, title, desc in topics_data:
        cursor.execute("SELECT id FROM topics WHERE subject_id = ? AND sequence_order = ?", (subject_id, seq))
        existing_topic = cursor.fetchone()
        if existing_topic:
            topic_id_map[seq] = existing_topic["id"]
        else:
            cursor.execute("""
                INSERT INTO topics (subject_id, title, sequence_order, description)
                VALUES (?, ?, ?, ?)
            """, (subject_id, title, seq, desc))
            topic_id_map[seq] = cursor.lastrowid

    print(f"[SEED] Seeded {len(topic_id_map)} topics.")

    # 3. 10 Diagnostic Questions
    cursor.execute("SELECT COUNT(*) as cnt FROM questions WHERE is_diagnostic = 1")
    if cursor.fetchone()["cnt"] == 0:
        diagnostic_questions = [
            # Basic Tier (Q1 - Q3)
            (
                topic_id_map[1], 1, "basic",
                "What will be the output of the following Python snippet?",
                "x = 5\ny = '10'\nprint(type(x), type(y))",
                "<class 'int'> <class 'int'>",
                "<class 'int'> <class 'str'>",
                "<class 'str'> <class 'int'>",
                "<class 'float'> <class 'str'>",
                "B",
                "In Python, 5 is an integer (int) while '10' enclosed in quotes is a string (str)."
            ),
            (
                topic_id_map[1], 1, "basic",
                "Which symbol is used for single-line comments in Python?",
                None,
                "//",
                "/* */",
                "#",
                "--",
                "C",
                "The hash symbol '#' begins a single-line comment in Python."
            ),
            (
                topic_id_map[2], 1, "basic",
                "What is the output of this conditional statement?",
                "score = 45\nif score >= 50:\n    print('Pass')\nelse:\n    print('Review')",
                "Pass",
                "Review",
                "SyntaxError",
                "None",
                "B",
                "Since 45 is less than 50, the condition evaluates to False and the else branch executes."
            ),
            # Intermediate Tier (Q4 - Q7)
            (
                topic_id_map[3], 1, "intermediate",
                "How many times will this loop print the value?",
                "for i in range(1, 6, 2):\n    print(i)",
                "2 times (1, 3)",
                "3 times (1, 3, 5)",
                "5 times (1, 2, 3, 4, 5)",
                "6 times",
                "B",
                "range(start, stop, step) generates 1, 3, 5. Stop value 6 is exclusive, so it executes 3 times."
            ),
            (
                topic_id_map[5], 1, "intermediate",
                "What is the result of applying the following list slice?",
                "nums = [10, 20, 30, 40, 50]\nprint(nums[1:4])",
                "[10, 20, 30]",
                "[20, 30, 40]",
                "[20, 30, 40, 50]",
                "[10, 30, 50]",
                "B",
                "Slicing [1:4] includes index 1, 2, and 3: [20, 30, 40]."
            ),
            (
                topic_id_map[5], 1, "intermediate",
                "What does the dictionary get() method return if the key does not exist and no default is specified?",
                "user = {'name': 'Alex'}\nprint(user.get('age'))",
                "KeyError",
                "0",
                "None",
                "False",
                "C",
                "dict.get(key) safely returns None if the key does not exist, avoiding a KeyError."
            ),
            (
                topic_id_map[4], 1, "intermediate",
                "What will the following function call output?",
                "def greet(name, msg='Hello'):\n    return f'{msg}, {name}!'\n\nprint(greet('Sam'))",
                "Hello, Sam!",
                "Sam, Hello!",
                "TypeError: missing required argument",
                "None",
                "A",
                "The argument 'msg' has a default value 'Hello', so passing only 'Sam' uses the default message."
            ),
            # Advanced Tier (Q8 - Q10)
            (
                topic_id_map[5], 1, "advanced",
                "What does this list comprehension evaluate to?",
                "squares = [x**2 for x in range(5) if x % 2 == 0]\nprint(squares)",
                "[0, 4, 16]",
                "[1, 9]",
                "[0, 1, 4, 9, 16]",
                "[4, 16]",
                "A",
                "Even numbers in range(5) are 0, 2, 4. Their squares are 0^2 = 0, 2^2 = 4, 4^2 = 16."
            ),
            (
                topic_id_map[4], 1, "advanced",
                "What will be the output of this code with exception handling?",
                "try:\n    val = int('python')\nexcept ValueError:\n    val = -1\nfinally:\n    val += 10\nprint(val)",
                "-1",
                "9",
                "10",
                "ValueError",
                "B",
                "int('python') raises ValueError, setting val = -1. The finally block always runs, adding 10: -1 + 10 = 9."
            ),
            (
                topic_id_map[4], 1, "advanced",
                "What is the result of using a lambda with map() here?",
                "data = [1, 2, 3]\nresult = list(map(lambda x: x * 3, data))\nprint(result)",
                "[3, 6, 9]",
                "[1, 4, 9]",
                "[3, 3, 3]",
                "[1, 2, 3, 1, 2, 3, 1, 2, 3]",
                "A",
                "map applies the anonymous lambda function (multiply by 3) to each element: 1*3=3, 2*3=6, 3*3=9."
            )
        ]

        for tid, is_diag, diff, qtext, code, oa, ob, oc, od, ans, exp in diagnostic_questions:
            cursor.execute("""
                INSERT INTO questions (
                    topic_id, is_diagnostic, difficulty_tier, question_text,
                    code_snippet, option_a, option_b, option_c, option_d,
                    correct_option, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tid, is_diag, diff, qtext, code, oa, ob, oc, od, ans, exp))
        print(f"[SEED] Seeded {len(diagnostic_questions)} diagnostic questions.")

    # 4. Seed Topic Micro-Assessment Questions (3 questions per topic = 15 questions)
    cursor.execute("SELECT COUNT(*) as cnt FROM questions WHERE is_diagnostic = 0")
    if cursor.fetchone()["cnt"] == 0:
        topic_questions = [
            # Topic 1: Syntax & Variables
            (topic_id_map[1], "basic", "Which identifier name is invalid in Python?", None, "user_name", "2nd_value", "_count", "TOTAL", "B", "Variable names cannot start with a digit."),
            (topic_id_map[1], "intermediate", "What is the result of 17 // 4 in Python?", None, "4.25", "4", "4.0", "1", "B", "// is the integer floor division operator."),
            (topic_id_map[1], "advanced", "What is the output of bool([]) and bool('False')?", None, "True, True", "False, False", "False, True", "True, False", "C", "An empty list is falsy, while any non-empty string is truthy."),
            
            # Topic 2: Control Flow
            (topic_id_map[2], "basic", "Which keyword is used for 'else if' in Python?", None, "elseif", "elsif", "elif", "case", "C", "Python uses 'elif' for chaining conditions."),
            (topic_id_map[2], "intermediate", "What will this expression return: not (5 > 2 and 3 == 4)?", None, "True", "False", "None", "Error", "A", "(5 > 2 and 3 == 4) is (True and False) = False. not False is True."),
            (topic_id_map[2], "advanced", "What is ternary conditional syntax in Python?", None, "cond ? a : b", "a if cond else b", "if cond then a else b", "cond(a, b)", "B", "Python ternary syntax is: value_if_true if condition else value_if_false."),

            # Topic 3: Loops
            (topic_id_map[3], "basic", "Which statement exits a loop immediately?", None, "continue", "skip", "break", "return", "C", "The 'break' statement terminates the innermost active loop."),
            (topic_id_map[3], "intermediate", "What does the 'continue' keyword do inside a loop?", None, "Exits the loop", "Restarts the program", "Skips to the next iteration", "Pauses for 1 second", "C", "'continue' stops the current iteration and jumps to the next iteration."),
            (topic_id_map[3], "advanced", "When does the 'else' clause of a Python for loop execute?", None, "Always after every loop", "Only if the loop was terminated with break", "Only if the loop finished without hitting a break", "Never", "C", "The else block of a loop executes only if the loop completed naturally without encountering a break."),

            # Topic 4: Functions
            (topic_id_map[4], "basic", "Which keyword is used to declare a function in Python?", None, "func", "function", "def", "define", "C", "Functions are defined using the 'def' keyword."),
            (topic_id_map[4], "intermediate", "What happens when a function does not have a return statement?", None, "Throws a compilation error", "Returns 0", "Returns None", "Returns undefined", "C", "Python functions implicitly return None if no return statement is reached."),
            (topic_id_map[4], "advanced", "What is the purpose of *args in a function parameter list?", None, "Accepts keyword arguments as a dictionary", "Accepts arbitrary positional arguments as a tuple", "Defines a pointer", "Forces type checking", "B", "*args packs arbitrary positional arguments into a tuple."),

            # Topic 5: Data Structures
            (topic_id_map[5], "basic", "Which of the following creates an empty dictionary?", None, "{}", "[]", "()", "set()", "A", "{} creates an empty dictionary. (set() is used for empty sets)."),
            (topic_id_map[5], "intermediate", "Which method removes and returns the last element of a list?", None, "delete()", "pop()", "remove()", "discard()", "B", "list.pop() removes and returns the element at the specified index, defaulting to the last element."),
            (topic_id_map[5], "advanced", "What is the key difference between lists and tuples?", None, "Lists are immutable; tuples are mutable", "Lists are mutable; tuples are immutable", "Tuples cannot store strings", "Lists have fixed size", "B", "Lists can be modified in-place (mutable); tuples cannot be modified once created (immutable).")
        ]

        for tid, diff, qtext, code, oa, ob, oc, od, ans, exp in topic_questions:
            cursor.execute("""
                INSERT INTO questions (
                    topic_id, is_diagnostic, difficulty_tier, question_text,
                    code_snippet, option_a, option_b, option_c, option_d,
                    correct_option, explanation
                ) VALUES (?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tid, diff, qtext, code, oa, ob, oc, od, ans, exp))
        print(f"[SEED] Seeded {len(topic_questions)} topic assessment questions.")

    # 5. Seed Adaptive Learning Materials (3 levels per topic: Basic, Intermediate, Advanced)
    cursor.execute("SELECT COUNT(*) as cnt FROM learning_materials")
    if cursor.fetchone()["cnt"] == 0:
        materials_data = [
            # Topic 1: Syntax & Variables
            (
                topic_id_map[1], "basic",
                "Foundational Python: Syntax, Types & First Steps",
                """# Welcome to Python Basics! 🚀
Python is an elegant, readable programming language.

### 1. Variables
In Python, you do not need to declare types manually. Just assign a value:
```python
age = 18            # Integer
price = 19.99       # Float
student_name = "Alex" # String
is_enrolled = True  # Boolean
```

### 2. Printing and Formatting
Use `print()` to output information to the console:
```python
print("Hello, " + student_name)
# Or modern f-strings:
print(f"Welcome {student_name}, your balance is ${price}")
```

### 3. Quick Rule
Variable names cannot start with numbers, cannot contain spaces, and are case-sensitive (`Score` != `score`).
""",
                "https://www.youtube.com/embed/kqtD5dpn9C8",
                "Python for Beginners - Variables and Types in 4 Minutes",
                4,
                "Variables store data; Python automatically detects data types; use f-strings for clean text output."
            ),
            (
                topic_id_map[1], "intermediate",
                "Practical Python: Type Casting, Memory & Formatting",
                """# Intermediate Syntax & Type Casting ⚙️

### 1. Explicit Type Conversion
User inputs or data feeds often arrive as strings. Always convert before arithmetic:
```python
raw_input = "42"
number = int(raw_input)
assert number + 8 == 50
```

### 2. The Identity vs Equality Trap
- `==` checks value equality.
- `is` checks memory identity (same object in memory).
```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True (same values)
print(a is b)  # False (different memory addresses)
```
""",
                "https://www.youtube.com/embed/Z1Yd7upQsXY",
                "Python Type Conversion & Identity Under the Hood",
                5,
                "Distinguish between == (equality) and is (identity); convert types explicitly to avoid TypeErrors."
            ),
            (
                topic_id_map[1], "advanced",
                "Advanced Python: Interning, Mutability & Bytecode",
                """# Advanced Syntax: Memory Model & Python Internals 🧠

### 1. Small Integer and String Interning
CPython pre-allocates integer objects in the range `[-5, 256]`:
```python
x = 250
y = 250
print(x is y)  # True, due to integer interning pool!
```

### 2. Scope & LEGB Rule
Variable resolution follows the LEGB hierarchy:
1. **L**ocal
2. **E**nclosing
3. **G**lobal
4. **B**uilt-in
""",
                "https://www.youtube.com/embed/C2fI2_f3V0Y",
                "Python Memory Management & Internals Deep Dive",
                7,
                "CPython optimizes memory through interning and reference counting; LEGB governs scope resolution."
            ),

            # Topic 2: Control Flow
            (
                topic_id_map[2], "basic",
                "Making Decisions: If, Elif, and Else Statements",
                """# Conditional Logic Made Easy 🚦
Programs make decisions using `if`, `elif`, and `else`.

### Structure
```python
temperature = 28

if temperature > 30:
    print("It's hot outside! Stay hydrated.")
elif temperature >= 20:
    print("Pleasant weather!")
else:
    print("It might be chilly, wear a jacket.")
```

### Important Rule: Indentation
Python relies on 4 spaces of indentation to denote blocks of code. Do not mix tabs and spaces!
""",
                "https://www.youtube.com/embed/DZwmZ8Usvnk",
                "Python Conditionals (if, elif, else) Visualized",
                4,
                "Conditionals run blocks when True; Indentation defines code blocks; elif allows multi-condition checks."
            ),
            (
                topic_id_map[2], "intermediate",
                "Boolean Algebra, Truthy/Falsy & Short-Circuit Evaluation",
                """# Boolean Logic & Short-Circuiting ⚡

### 1. Truthy and Falsy Values
In Python, empty structures and zeroes evaluate to `False`:
- Falsy: `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None`, `False`
- Everything else is **Truthy**.

```python
cart = []
if not cart:
    print("Your shopping cart is empty!")
```

### 2. Short-Circuit Evaluation
Python stops evaluating boolean expressions as soon as the result is certain:
```python
# If user is None, user.name is never evaluated, preventing AttributeError!
if user is not None and user.is_active:
    grant_access()
```
""",
                "https://www.youtube.com/embed/AWek49wXGzI",
                "Python Short-Circuit Evaluation & Truthiness",
                5,
                "Empty objects are falsy; short-circuit evaluation prevents runtime errors like NoneType attribute checks."
            ),
            (
                topic_id_map[2], "advanced",
                "Pattern Matching (Python 3.10+) & Guard Clauses",
                """# Structural Pattern Matching & Clean Guard Clauses 🛡️

### 1. Structural Pattern Matching
Python 3.10+ provides `match/case` with destructuring:
```python
def handle_command(command):
    match command.split():
        case ["go", direction]:
            print(f"Moving {direction}")
        case ["attack", target, *weapons]:
            print(f"Attacking {target} using {weapons}")
        case _:
            print("Unknown command")
```

### 2. Guard Clauses over Deep Nesting
Always invert conditions early to exit functions quickly and eliminate arrow anti-patterns.
""",
                "https://www.youtube.com/embed/scNWnk_F_gE",
                "Structural Pattern Matching in Modern Python",
                6,
                "Match/case provides expressive destructuring; guard clauses flatten deeply nested conditional logic."
            ),

            # Topic 3: Loops & Iterations
            (
                topic_id_map[3], "basic",
                "Repeating Tasks: For and While Loops",
                """# Loops in Python 🔄

### 1. The For Loop with range()
When you know how many times to repeat:
```python
for count in range(1, 4):
    print(f"Lap {count} completed")
# Outputs: Lap 1 completed, Lap 2 completed, Lap 3 completed
```

### 2. The While Loop
Runs as long as a condition remains true:
```python
lives = 3
while lives > 0:
    print(f"Player has {lives} lives remaining")
    lives -= 1
```
""",
                "https://www.youtube.com/embed/6iF8Xb7Z3wQ",
                "Python Loops: For & While Explained Step-by-Step",
                5,
                "Use 'for' for collections and ranges; use 'while' when waiting for a condition; always update loop counters."
            ),
            (
                topic_id_map[3], "intermediate",
                "Loop Control: break, continue, and enumerate()",
                """# Mastering Loop Controls 🎯

### 1. break vs continue
- `break`: Aborts the entire loop immediately.
- `continue`: Skips the rest of the current iteration and jumps to the next.

### 2. Pythonic Indexing with enumerate()
Never use `range(len(items))`! Use `enumerate()` instead:
```python
colors = ["red", "green", "blue"]
for index, color in enumerate(colors, start=1):
    print(f"#{index}: {color}")
```

### 3. Iterating Multiple Lists with zip()
```python
names = ["Alice", "Bob"]
scores = [95, 88]
for name, score in zip(names, scores):
    print(f"{name} scored {score}")
```
""",
                "https://www.youtube.com/embed/94UHCEmprCY",
                "Pythonic Loops: Enumerate, Zip & Controls",
                5,
                "Use enumerate() for index-item pairs; use zip() to iterate collections in parallel; break/continue control flow."
            ),
            (
                topic_id_map[3], "advanced",
                "Generators, Iterators Protocol & itertools",
                """# Generators & Memory Efficiency 🚀

### 1. Yield and Memory Footprint
A generator computes items on-demand, consuming $O(1)$ memory instead of storing millions of items in RAM:
```python
def fibonacci(limit):
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b

for val in fibonacci(5):
    print(val) # 0, 1, 1, 2, 3
```

### 2. The Iterator Protocol
Any class implementing `__iter__()` and `__next__()` is a Python iterator.
""",
                "https://www.youtube.com/embed/bD05uGo_sVI",
                "Python Generators and Iterators Architecture",
                7,
                "Generators yield values lazily to achieve O(1) memory complexity; iterators implement __iter__ and __next__."
            ),

            # Topic 4: Functions & Scope
            (
                topic_id_map[4], "basic",
                "Writing Modular Code with Functions",
                """# Functions: Reusable Code Blocks 📦

### 1. Defining a Function
```python
def calculate_area(width, height):
    area = width * height
    return area

# Call the function
result = calculate_area(5, 10)
print(f"Total Area: {result}") # 50
```

### 2. Why Functions?
- **DRY** (Don't Repeat Yourself)
- Easier debugging
- Modular, testable code
""",
                "https://www.youtube.com/embed/9Os0o3wzS_I",
                "Functions in Python for Beginners",
                4,
                "Functions take inputs (parameters) and return outputs; they organize code into reusable blocks."
            ),
            (
                topic_id_map[4], "intermediate",
                "Default Arguments, *args, and **kwargs",
                """# Flexible Functions in Python 🛠️

### 1. Default Parameters
```python
def power(base, exponent=2):
    return base ** exponent

print(power(4))    # 16 (4^2)
print(power(4, 3)) # 64 (4^3)
```
*Warning: Never use a mutable object (like a list `[]`) as a default parameter!*

### 2. Variable Arguments
- `*args`: Collects positional arguments into a tuple.
- `**kwargs`: Collects keyword arguments into a dictionary.
```python
def build_profile(username, **user_info):
    user_info["username"] = username
    return user_info
```
""",
                "https://www.youtube.com/embed/WcdaXb7j10E",
                "Mastering *args and **kwargs in Python",
                5,
                "Never use mutable default arguments; *args handles variable positional arguments; **kwargs handles keyword dicts."
            ),
            (
                topic_id_map[4], "advanced",
                "Closures, Decorators & First-Class Functions",
                """# Closures & Function Decorators 🎨

Functions in Python are first-class citizens: they can be passed as arguments and returned from other functions.

### Building a Custom Decorator
```python
import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.4f}s")
        return result
    return wrapper

@timing_decorator
def heavy_calculation():
    return sum(i * i for i in range(100000))
```
""",
                "https://www.youtube.com/embed/FsAPt_9Bf3U",
                "Python Decorators in 10 Minutes",
                6,
                "Decorators wrap and extend function behaviors cleanly; closures remember their enclosing scope state."
            ),

            # Topic 5: Data Structures
            (
                topic_id_map[5], "basic",
                "Lists, Tuples & Dictionaries Explained",
                """# Essential Data Structures 📚

### 1. Lists (Ordered & Mutable)
```python
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")
print(fruits[0]) # "apple"
```

### 2. Dictionaries (Key-Value Pairs)
```python
student = {
    "name": "Sarah",
    "grade": "A",
    "points": 95
}
print(student["name"]) # "Sarah"
```
""",
                "https://www.youtube.com/embed/tw7ror9x32s",
                "Python Lists and Dictionaries for Beginners",
                5,
                "Lists store ordered items; Dictionaries store key-value lookups; Tuples store fixed immutable data."
            ),
            (
                topic_id_map[5], "intermediate",
                "List Comprehensions & Dictionary Methods",
                """# Fast Data Processing with Comprehensions ⚡

### 1. List Comprehensions
Transform data in one clean, readable line:
```python
numbers = [1, 2, 3, 4, 5, 6]
evens = [n for n in numbers if n % 2 == 0]
# [2, 4, 6]
```

### 2. Safe Dictionary Access
Always prefer `.get()` to avoid crashing your application:
```python
config = {"theme": "dark"}
# If "timeout" is missing, returns 30 instead of raising KeyError:
timeout = config.get("timeout", 30)
```
""",
                "https://www.youtube.com/embed/3dt4xZ41V74",
                "Python List Comprehensions & Dict Tricks",
                5,
                "Comprehensions provide fast concise list creation; dict.get(key, default) avoids KeyError exceptions."
            ),
            (
                topic_id_map[5], "advanced",
                "Collections Module & Big-O Complexity",
                """# High-Performance Data Structures 🏎️

### 1. Time Complexities to Remember
- List lookup by index: $O(1)$
- List search `in`: $O(n)$
- Dictionary lookup by key: $O(1)$ average!
- Set membership test: $O(1)$ average!

### 2. Specialized Collections
```python
from collections import defaultdict, deque, Counter

# Deque: O(1) appends and pops from both ends
queue = deque([1, 2, 3])
queue.appendleft(0)

# Counter: Instant frequency counting
counts = Counter("abracadabra")
print(counts["a"]) # 5
```
""",
                "https://www.youtube.com/embed/daefaLgNkw0",
                "Python Collections & Time Complexities",
                6,
                "Dicts and sets offer O(1) lookups; collections.deque enables fast FIFO queues; Counter simplifies frequency counts."
            )
        ]

        for tid, tier, title, notes, vurl, vtitle, dur, takeaways in materials_data:
            cursor.execute("""
                INSERT INTO learning_materials (
                    topic_id, level_tier, title, notes_markdown,
                    video_url, video_title, duration_minutes, key_takeaways
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tid, tier, title, notes, vurl, vtitle, dur, takeaways))
        print(f"[SEED] Seeded {len(materials_data)} adaptive learning material modules.")

    conn.commit()
    conn.close()
    print("[SEED] Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
