# test_agent.py
from src.ingest.pdf_loader import load_and_chunk_pdfs
from src.ingest.sql_loader import load_sqlite_schema_and_samples
from src.retrieval.vector_store import load_or_create_vector_store, search_vector_store
from src.retrieval.sql_retriever import generate_sql_with_gemini, execute_sql_safe
from src.agents.hybrid_rag_agent import hybrid_rag_answer

def end_to_end_hybrid_rag(user_query: str) -> str:
    print(f"🔍 User query: {user_query}")
    
    # 1. Unstructured retrieval
    pdf_chunks = load_and_chunk_pdfs()
    vectorstore = load_or_create_vector_store(pdf_chunks)
    retrieved_docs = search_vector_store(user_query, vectorstore, k=2)
    
    # 2. Structured retrieval
    schema_info = load_sqlite_schema_and_samples()
    generated_sql = generate_sql_with_gemini(user_query, schema_info)
    sql_result = []
    if generated_sql:
        try:
            sql_result = execute_sql_safe(generated_sql)
        except Exception as e:
            print(f"⚠️ SQL execution failed: {e}")
            generated_sql = ""
    
    # 3. Fusion & final answer
    final_answer = hybrid_rag_answer(
        user_query=user_query,
        pdf_chunks=retrieved_docs,
        sql_result=sql_result,
        generated_sql=generated_sql
    )
    
    return final_answer

if __name__ == "__main__":
    query = "Which artist has the most albums, and what does the document say about them?"
    answer = end_to_end_hybrid_rag(query)
    print("\n" + "="*60)
    print("🤖 Final Answer:")
    print(answer)
    print("="*60)