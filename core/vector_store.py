import os
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

VECTOR_STORE_PATH = "vector_db/faiss_index"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # Lightweight BGE model

def get_embeddings():
    """Get lightweight BGE embeddings."""
    return HuggingFaceBgeEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

def build_vector_store(transcript: str):
    """Build FAISS vector store from transcript."""
    print("Building vector store...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunk, metadata={'chunk_index': i})
        for i, chunk in enumerate(chunks)
    ]

    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(
        documents=docs,
        embedding=embeddings
    )

    # Save to disk
    os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
    vector_store.save_local(VECTOR_STORE_PATH)
    
    print(f"✓ Vector store built with {len(chunks)} chunks")
    return vector_store


def load_vector_store():
    """Load FAISS vector store from disk."""
    embeddings = get_embeddings()
    vector_store = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_store


def get_retriever(vector_store, k: int = 4):
    """Get retriever from vector store."""
    return vector_store.as_retriever(
        search_type='similarity',
        search_kwargs={"k": k}
    )

