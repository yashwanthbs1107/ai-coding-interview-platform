from database import SessionLocal

from models import Problem

from redis_client import redis_client

import redis

import json

db = SessionLocal()



problems = [

    # =========================================================

    # BINARY SEARCH

    # =========================================================



    {

        "problem": "Binary Search",

        "topic": "Binary Search",

        "difficulty": "Easy",

        "description": "Given a sorted array of integers and a target value, return the index of the target if it exists. Otherwise, return -1.",

        "examples": [

            {"input": "nums = [1,2,3,4,5], target = 3", "output": "2"},

            {"input": "nums = [1,2,3,4,5], target = 6", "output": "-1"}

        ],

        "constraints": [

            "1 <= nums.length <= 10000",

            "-10000 <= nums[i] <= 10000",

            "nums is sorted in ascending order",

            "-10000 <= target <= 10000"

        ],

        "test_cases": [

            {"input": "5\n1 2 3 4 5\n3", "expected_output": "2"},

            {"input": "5\n1 2 3 4 5\n6", "expected_output": "-1"},

            {"input": "1\n10\n10", "expected_output": "0"}

        ]

    },



    {

        "problem": "Search Insert Position",

        "topic": "Binary Search",

        "difficulty": "Easy",

        "description": "Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where the target should be inserted to maintain sorted order.",

        "examples": [

            {"input": "nums = [1,3,5,6], target = 5", "output": "2"},

            {"input": "nums = [1,3,5,6], target = 2", "output": "1"},

            {"input": "nums = [1,3,5,6], target = 7", "output": "4"}

        ],

        "constraints": [

            "1 <= nums.length <= 10000",

            "-10000 <= nums[i] <= 10000",

            "nums contains distinct values",

            "nums is sorted in ascending order"

        ],

        "test_cases": [

            {"input": "4\n1 3 5 6\n5", "expected_output": "2"},

            {"input": "4\n1 3 5 6\n2", "expected_output": "1"},

            {"input": "4\n1 3 5 6\n7", "expected_output": "4"}

        ]

    },



    {

        "problem": "First and Last Position",

        "topic": "Binary Search",

        "difficulty": "Medium",

        "description": "Given a sorted array of integers that may contain duplicates, find the starting and ending position of a given target value. Return [-1, -1] if the target is not present.",

        "examples": [

            {"input": "nums = [5,7,7,8,8,10], target = 8", "output": "[3,4]"},

            {"input": "nums = [5,7,7,8,8,10], target = 6", "output": "[-1,-1]"}

        ],

        "constraints": [

            "0 <= nums.length <= 10000",

            "-10^9 <= nums[i] <= 10^9",

            "nums is sorted in non-decreasing order",

            "-10^9 <= target <= 10^9"

        ],

        "test_cases": [

            {"input": "6\n5 7 7 8 8 10\n8", "expected_output": "3 4"},

            {"input": "6\n5 7 7 8 8 10\n6", "expected_output": "-1 -1"},

            {"input": "5\n2 2 2 2 2\n2", "expected_output": "0 4"}

        ]

    },



    # =========================================================

    # TWO POINTERS

    # =========================================================



    {

        "problem": "Two Sum II",

        "topic": "Two Pointers",

        "difficulty": "Medium",

        "description": "Given a 1-indexed sorted array of integers and a target value, find two numbers that add up to the target. Return their 1-based indices.",

        "examples": [

            {"input": "numbers = [2,7,11,15], target = 9", "output": "[1,2]"},

            {"input": "numbers = [2,3,4], target = 6", "output": "[1,3]"}

        ],

        "constraints": [

            "2 <= numbers.length <= 10000",

            "-1000 <= numbers[i] <= 1000",

            "numbers is sorted in non-decreasing order",

            "Exactly one solution exists"

        ],

        "test_cases": [

            {"input": "4\n2 7 11 15\n9", "expected_output": "1 2"},

            {"input": "3\n2 3 4\n6", "expected_output": "1 3"},

            {"input": "2\n-1 5\n4", "expected_output": "1 2"}

        ]

    },



    {

        "problem": "3Sum",

        "topic": "Two Pointers",

        "difficulty": "Medium",

        "description": "Given an integer array, return all unique triplets [a,b,c] such that a + b + c = 0.",

        "examples": [

            {"input": "nums = [-1,0,1,2,-1,-4]", "output": "[[-1,-1,2],[-1,0,1]]"},

            {"input": "nums = [0,1,1]", "output": "[]"}

        ],

        "constraints": [

            "3 <= nums.length <= 3000",

            "-10^5 <= nums[i] <= 10^5"

        ],

        "test_cases": [

            {"input": "6\n-1 0 1 2 -1 -4", "expected_output": "-1 -1 2\n-1 0 1"},

            {"input": "3\n0 1 1", "expected_output": ""},

            {"input": "3\n0 0 0", "expected_output": "0 0 0"}

        ]

    },



    {

        "problem": "Remove Duplicates from Sorted Array",

        "topic": "Two Pointers",

        "difficulty": "Easy",

        "description": "Given a sorted array, remove duplicates in-place so that each unique element appears only once. Return the number of unique elements.",

        "examples": [

            {"input": "nums = [1,1,2]", "output": "2"},

            {"input": "nums = [0,0,1,1,1,2,2,3,3,4]", "output": "5"}

        ],

        "constraints": [

            "1 <= nums.length <= 30000",

            "-100 <= nums[i] <= 100",

            "nums is sorted in non-decreasing order"

        ],

        "test_cases": [

            {"input": "3\n1 1 2", "expected_output": "2"},

            {"input": "5\n1 2 3 4 5", "expected_output": "5"},

            {"input": "5\n2 2 2 2 2", "expected_output": "1"}

        ]

    },



    # =========================================================

    # SLIDING WINDOW

    # =========================================================



    {

        "problem": "Maximum Sum Subarray",

        "topic": "Sliding Window",

        "difficulty": "Easy",

        "description": "Given an array of positive integers and an integer k, find the maximum sum of any contiguous subarray of size k.",

        "examples": [

            {"input": "nums = [2,1,5,1,3,2], k = 3", "output": "9"},

            {"input": "nums = [2,3,4,1,5], k = 2", "output": "7"}

        ],

        "constraints": [

            "1 <= nums.length <= 100000",

            "1 <= k <= nums.length",

            "1 <= nums[i] <= 10000"

        ],

        "test_cases": [

            {"input": "6\n2 1 5 1 3 2\n3", "expected_output": "9"},

            {"input": "5\n2 3 4 1 5\n2", "expected_output": "7"},

            {"input": "4\n1 2 3 4\n1", "expected_output": "4"}

        ]

    },



    {

        "problem": "Longest Substring Without Repeating Characters",

        "topic": "Sliding Window",

        "difficulty": "Medium",

        "description": "Given a string, find the length of the longest substring without repeating characters.",

        "examples": [

            {"input": "s = abcabcbb", "output": "3"},

            {"input": "s = bbbbb", "output": "1"},

            {"input": "s = pwwkew", "output": "3"}

        ],

        "constraints": [

            "0 <= s.length <= 50000",

            "s consists of English letters, digits, symbols and spaces"

        ],

        "test_cases": [

            {"input": "abcabcbb", "expected_output": "3"},

            {"input": "bbbbb", "expected_output": "1"},

            {"input": "pwwkew", "expected_output": "3"}

        ]

    },



    {

        "problem": "Minimum Size Subarray Sum",

        "topic": "Sliding Window",

        "difficulty": "Medium",

        "description": "Given an array of positive integers and a positive integer target, return the minimal length of a contiguous subarray whose sum is greater than or equal to target. Return 0 if no such subarray exists.",

        "examples": [

            {"input": "target = 7, nums = [2,3,1,2,4,3]", "output": "2"},

            {"input": "target = 4, nums = [1,4,4]", "output": "1"}

        ],

        "constraints": [

            "1 <= target <= 10^9",

            "1 <= nums.length <= 100000",

            "1 <= nums[i] <= 100000"

        ],

        "test_cases": [

            {"input": "7\n6\n2 3 1 2 4 3", "expected_output": "2"},

            {"input": "4\n3\n1 4 4", "expected_output": "1"},

            {"input": "100\n3\n1 2 3", "expected_output": "0"}

        ]

    },



    # =========================================================

    # ARRAYS

    # =========================================================



    {

        "problem": "Maximum Subarray",

        "topic": "Arrays",

        "difficulty": "Medium",

        "description": "Given an integer array, find the contiguous subarray with the largest sum and return its sum.",

        "examples": [

            {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6"},

            {"input": "nums = [1]", "output": "1"}

        ],

        "constraints": [

            "1 <= nums.length <= 100000",

            "-10^4 <= nums[i] <= 10^4"

        ],

        "test_cases": [

            {"input": "9\n-2 1 -3 4 -1 2 1 -5 4", "expected_output": "6"},

            {"input": "1\n1", "expected_output": "1"},

            {"input": "3\n-1 -2 -3", "expected_output": "-1"}

        ]

    },



    {

        "problem": "Best Time to Buy and Sell Stock",

        "topic": "Arrays",

        "difficulty": "Easy",

        "description": "Given an array where prices[i] is the price of a stock on day i, find the maximum profit from buying on one day and selling on a later day.",

        "examples": [

            {"input": "prices = [7,1,5,3,6,4]", "output": "5"},

            {"input": "prices = [7,6,4,3,1]", "output": "0"}

        ],

        "constraints": [

            "1 <= prices.length <= 100000",

            "0 <= prices[i] <= 100000"

        ],

        "test_cases": [

            {"input": "6\n7 1 5 3 6 4", "expected_output": "5"},

            {"input": "5\n7 6 4 3 1", "expected_output": "0"},

            {"input": "2\n1 2", "expected_output": "1"}

        ]

    },



    {

        "problem": "Move Zeroes",

        "topic": "Arrays",

        "difficulty": "Easy",

        "description": "Given an integer array, move all zeroes to the end while maintaining the relative order of the non-zero elements.",

        "examples": [

            {"input": "nums = [0,1,0,3,12]", "output": "[1,3,12,0,0]"},

            {"input": "nums = [0]", "output": "[0]"}

        ],

        "constraints": [

            "1 <= nums.length <= 10000",

            "-10^9 <= nums[i] <= 10^9"

        ],

        "test_cases": [

            {"input": "5\n0 1 0 3 12", "expected_output": "1 3 12 0 0"},

            {"input": "1\n0", "expected_output": "0"},

            {"input": "4\n1 2 3 4", "expected_output": "1 2 3 4"}

        ]

    },



    # =========================================================

    # HASHING

    # =========================================================



    {

        "problem": "Two Sum",

        "topic": "Hashing",

        "difficulty": "Easy",

        "description": "Given an array of integers and a target value, return the indices of two numbers that add up to the target.",

        "examples": [

            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},

            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"}

        ],

        "constraints": [

            "2 <= nums.length <= 10000",

            "-10^9 <= nums[i] <= 10^9",

            "-10^9 <= target <= 10^9",

            "Exactly one solution exists"

        ],

        "test_cases": [

            {"input": "4\n2 7 11 15\n9", "expected_output": "0 1"},

            {"input": "3\n3 2 4\n6", "expected_output": "1 2"},

            {"input": "2\n3 3\n6", "expected_output": "0 1"}

        ]

    },



    {

        "problem": "Majority Element",

        "topic": "Hashing",

        "difficulty": "Easy",

        "description": "Given an array of integers, return the element that appears more than half of the time.",

        "examples": [

            {"input": "nums = [3,2,3]", "output": "3"},

            {"input": "nums = [2,2,1,1,1,2,2]", "output": "2"}

        ],

        "constraints": [

            "1 <= nums.length <= 50000",

            "-10^9 <= nums[i] <= 10^9",

            "A majority element always exists"

        ],

        "test_cases": [

            {"input": "3\n3 2 3", "expected_output": "3"},

            {"input": "7\n2 2 1 1 1 2 2", "expected_output": "2"},

            {"input": "1\n5", "expected_output": "5"}

        ]

    },



    {

        "problem": "Contains Duplicate",

        "topic": "Hashing",

        "difficulty": "Easy",

        "description": "Given an integer array, return true if any value appears at least twice, otherwise return false.",

        "examples": [

            {"input": "nums = [1,2,3,1]", "output": "true"},

            {"input": "nums = [1,2,3,4]", "output": "false"}

        ],

        "constraints": [

            "1 <= nums.length <= 100000",

            "-10^9 <= nums[i] <= 10^9"

        ],

        "test_cases": [

            {"input": "4\n1 2 3 1", "expected_output": "true"},

            {"input": "4\n1 2 3 4", "expected_output": "false"},

            {"input": "3\n1 1 1", "expected_output": "true"}

        ]

    },



    # =========================================================

    # STACK

    # =========================================================



    {

        "problem": "Valid Parentheses",

        "topic": "Stack",

        "difficulty": "Easy",

        "description": "Given a string containing parentheses, brackets and braces, determine whether the input string is valid.",

        "examples": [

            {"input": "s = ()", "output": "true"},

            {"input": "s = ()[]{}", "output": "true"},

            {"input": "s = (]", "output": "false"}

        ],

        "constraints": [

            "1 <= s.length <= 10000",

            "s consists only of parentheses, brackets and braces"

        ],

        "test_cases": [

            {"input": "()", "expected_output": "true"},

            {"input": "()[]{}", "expected_output": "true"},

            {"input": "(]", "expected_output": "false"}

        ]

    },



    {

        "problem": "Min Stack",

        "topic": "Stack",

        "difficulty": "Medium",

        "description": "Design a stack that supports push, pop, top and retrieving the minimum element in constant time.",

        "examples": [

            {"input": "push(-2), push(0), push(-3), getMin()", "output": "-3"},

            {"input": "pop(), top(), getMin()", "output": "0, -2"}

        ],

        "constraints": [

            "Operations are push, pop, top and getMin",

            "Values are integers",

            "All operations should run in O(1)"

        ],

        "test_cases": [

            {

                "input": "7\npush -2\npush 0\npush -3\ngetMin\npop\ntop\ngetMin",

                "expected_output": "-3\n0\n-2"

            }

        ]

    },



    {

        "problem": "Next Greater Element",

        "topic": "Stack",

        "difficulty": "Medium",

        "description": "Given an array, find the next greater element for every element. If no greater element exists, return -1.",

        "examples": [

            {"input": "nums = [4,5,2,10]", "output": "[5,10,10,-1]"},

            {"input": "nums = [1,3,2,4]", "output": "[3,4,4,-1]"}

        ],

        "constraints": [

            "1 <= nums.length <= 10000",

            "-10^9 <= nums[i] <= 10^9"

        ],

        "test_cases": [

            {"input": "4\n4 5 2 10", "expected_output": "5 10 10 -1"},

            {"input": "4\n1 3 2 4", "expected_output": "3 4 4 -1"},

            {"input": "3\n5 4 3", "expected_output": "-1 -1 -1"}

        ]

    },



    # =========================================================

    # LINKED LIST

    # =========================================================



    {

        "problem": "Reverse Linked List",

        "topic": "Linked List",

        "difficulty": "Easy",

        "description": "Given the head of a singly linked list, reverse the list and return the new head.",

        "examples": [

            {"input": "head = [1,2,3,4,5]", "output": "[5,4,3,2,1]"},

            {"input": "head = [1,2]", "output": "[2,1]"}

        ],

        "constraints": [

            "0 <= number of nodes <= 5000",

            "-5000 <= Node.val <= 5000"

        ],

        "test_cases": [

            {"input": "5\n1 2 3 4 5", "expected_output": "5 4 3 2 1"},

            {"input": "2\n1 2", "expected_output": "2 1"},

            {"input": "1\n10", "expected_output": "10"}

        ]

    },



    {

        "problem": "Middle of the Linked List",

        "topic": "Linked List",

        "difficulty": "Easy",

        "description": "Given the head of a singly linked list, return the middle node. If there are two middle nodes, return the second middle node.",

        "examples": [

            {"input": "head = [1,2,3,4,5]", "output": "3"},

            {"input": "head = [1,2,3,4,5,6]", "output": "4"}

        ],

        "constraints": [

            "1 <= number of nodes <= 100",

            "1 <= Node.val <= 100"

        ],

        "test_cases": [

            {"input": "5\n1 2 3 4 5", "expected_output": "3"},

            {"input": "6\n1 2 3 4 5 6", "expected_output": "4"},

            {"input": "1\n10", "expected_output": "10"}

        ]

    },



    {

        "problem": "Merge Two Sorted Lists",

        "topic": "Linked List",

        "difficulty": "Easy",

        "description": "Merge two sorted linked lists and return the head of the merged sorted list.",

        "examples": [

            {"input": "list1 = [1,2,4], list2 = [1,3,4]", "output": "[1,1,2,3,4,4]"},

            {"input": "list1 = [], list2 = [0]", "output": "[0]"}

        ],

        "constraints": [

            "0 <= number of nodes in each list <= 50",

            "-100 <= Node.val <= 100",

            "Both lists are sorted in non-decreasing order"

        ],

        "test_cases": [

            {"input": "3\n1 2 4\n3\n1 3 4", "expected_output": "1 1 2 3 4 4"},

            {"input": "0\n\n1\n0", "expected_output": "0"},

            {"input": "2\n1 2\n2\n3 4", "expected_output": "1 2 3 4"}

        ]

    }

]

try:
    for data in problems:
        existing = (
            db.query(Problem)
            .filter(Problem.problem == data["problem"])
            .first()
        )

        if existing:
            existing.topic = data["topic"]
            existing.difficulty = data["difficulty"]
            existing.description = data["description"]
            existing.examples = json.dumps(data["examples"])
            existing.constraints = json.dumps(data["constraints"])
            existing.test_cases = json.dumps(data["test_cases"])
        else:
            new_problem = Problem(
                problem=data["problem"],
                topic=data["topic"],
                difficulty=data["difficulty"],
                description=data["description"],
                examples=json.dumps(data["examples"]),
                constraints=json.dumps(data["constraints"]),
                test_cases=json.dumps(data["test_cases"]),
            )
            db.add(new_problem)

    # Commit all inserts/updates together.
    db.commit()

    # Invalidate cached problem-list responses after the DB commit succeeds.
    try:
        for key in redis_client.scan_iter(match="problems:*"):
            redis_client.delete(key)
    except redis.RedisError:
        print("Warning: Redis unavailable. Cache will expire naturally.")

    print(f"{len(problems)} problems seeded successfully!")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()


print("no error found")