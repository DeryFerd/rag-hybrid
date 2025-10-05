# src/ingest/pdf_loader.py
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_and_chunk_pdfs(pdf_dir: str = "data/pdf", chunk_size: int = 512, chunk_overlap: int = 50) -> List[Document]:
    """
    Load all PDFs in a directory, extract text, and split into chunks.
    Returns list of LangChain Document objects.
    """
    documents = []
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(pdf_dir, filename)
            print(f"Loading PDF: {filepath}")
            loader = PyPDFLoader(filepath)
            pages = loader.load()
            documents.extend(pages)
    
    if not documents:
        print("⚠️ No PDFs found in data/pdf/")
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")
    return chunks