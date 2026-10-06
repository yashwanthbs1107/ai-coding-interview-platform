from ai_service import ask_gemini

code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
"""

prompt = f"""
Analyze the following coding solution.

Code:
{code}

Tell me:
1. What approach is being used?
2. What is the time complexity?
3. What is the space complexity?
4. Is there anything that could be improved?
"""

response = ask_gemini(prompt)

print(response)