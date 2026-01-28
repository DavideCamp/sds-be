def build_prompt(retrieve_chunks, question):
    context = "\n".join([c.text for c in retrieve_chunks])
    return f"""
You are a company assistant.
Use only the context.

Context:
{context}

Question:
{question}
"""


def build_prompt_for_score(retrieve_chunks, question):

    score = [c.score for c in retrieve_chunks]
    text = [c.text for c in retrieve_chunks]
    d = dict(zip(score, text))
    return f"""
{question}
{d}
    """