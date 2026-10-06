from rag_service import get_rag_context

query = "How does the sliding window technique work?"
context = get_rag_context(query)

print("RETRIEVED CONTEXT:")
print(context)