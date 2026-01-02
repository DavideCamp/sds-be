from rag_engine.retrieval import retrieve_chunks
from rag_engine.prompting import build_prompt
from rag_engine.retrieval import hybrid_search

def rag_answer(question, user):
    res = hybrid_search(question, user.id)
    chunks = retrieve_chunks(question, user)
    prompt = build_prompt(chunks, question)
    
    context = "\n".join([c["text"] for c in chunks])


    # per ora mock
    return "This is a placeholder answer based on documents. Context: " + context
