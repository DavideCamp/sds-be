from rag_engine.prompting import build_prompt, build_prompt_for_score
from rag_engine.search import SearchRag


def rag_answer(question, user):
    search = SearchRag()
    semantic_chunks = search.semantic_search(query=question, user_id=user.id)
    prompt = build_prompt_for_score(semantic_chunks, question)
    


    # per ora mock
    return "These are the answers: {prompt} ".format(prompt=prompt)
