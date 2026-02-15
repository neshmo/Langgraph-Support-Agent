from app.services.vectorstore import get_vectorstore

def add_knowledge_document(text: str, metadata: dict):
    """
    Add a new document to the knowledge base
    """
    vectorstore = get_vectorstore()
    vectorstore.add_texts(
        texts=[text],
        metadatas=[metadata]
    )


def search_knowledge_base(query: str, k: int = 3):
    """
    Retrieve relevant docs for a support query
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)

    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in results
    ]
