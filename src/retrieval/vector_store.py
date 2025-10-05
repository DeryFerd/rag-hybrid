# src/retrieval/vector_store.py
import os
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_vector_store(documents: List[Document], persist_dir: str = "data/vectorstore") -> FAISS:
    """
    Build FAISS vector store from documents using sentence-transformers.
    """
    if not documents:
        raise ValueError("No documents provided to build vector store.")
    
    # Use a lightweight, offline embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    print("🔍 Generating embeddings and building FAISS index...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Optional: save to disk
    os.makedirs(persist_dir, exist_ok=True)
    vectorstore.save_local(persist_dir)
    print(f"✅ Vector store saved to {persist_dir}")
    return vectorstore

def load_or_create_vector_store(documents: List[Document], persist_dir: str = "data/vectorstore") -> FAISS:
    """
    Load existing FAISS index or create new one.
    """
    if os.path.exists(persist_dir):
        print("📂 Loading existing FAISS index...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        return FAISS.load_local(persist_dir, embeddings, allow_dangerous_deserialization=True)
    else:
        return build_vector_store(documents, persist_dir)

def search_vector_store(query: str, vectorstore: FAISS, k: int = 3) -> List[Document]:
    """
    Search vector store and return top-k relevant documents.
    """
    return vectorstore.similarity_search(query, k=k)