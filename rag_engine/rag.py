from rag_engine.retrieval import retrieve_chunks
from rag_engine.prompting import build_prompt

def rag_answer(question, user):
    chunks = retrieve_chunks(question, user)
    prompt = build_prompt(chunks, question)

    # per ora mock
    return "This is a placeholder answer based on documents."
