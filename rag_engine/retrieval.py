from rag_engine.weaviate_client import WeaviateClient
def retrieve_chunks(query, user):
    # per ora stub
    return ["Example company policy text"]



def hybrid_search(query, user_id):
    return WeaviateClient().query.get("Chunk", ["text"]) \
        .with_where({
            "path": ["user_id"],
            "operator": "Equal",
            "valueInt": user_id
        }) \
        .with_hybrid(query=query, alpha=0.5) \
        .with_limit(5) \
        .do()
