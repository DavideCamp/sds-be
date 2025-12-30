def build_prompt(chunks, question):
    context = "\n".join(chunks)
    return f"""
You are a company assistant.
Use only the context.

Context:
{context}

Question:
{question}
"""
