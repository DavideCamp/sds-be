from rag_engine.mongodb_client import MongoDBClient
def retrieve_chunks(query, user):
    # per ora stub
    return ["Example company policy text"]



def hybrid_search(query, user_id):
    client = MongoDBClient()
    return client.find_chunks_by_user(user_id, limit=5)
