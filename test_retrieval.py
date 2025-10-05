# test_retrieval.py
from src.ingest.pdf_loader import load_and_chunk_pdfs
from src.ingest.sql_loader import load_sqlite_schema_and_samples
from src.retrieval.vector_store import load_or_create_vector_store, search_vector_store
from src.retrieval.sql_retriever import generate_sql_with_gemini, execute_sql_safe

def test_unstructured_retrieval():
    print("\n🔍 Testing Unstructured (PDF) Retrieval...")
    chunks = load_and_chunk_pdfs()
    if not chunks:
        print("⚠️ No PDF chunks found.")
        return []
    
    vectorstore = load_or_create_vector_store(chunks)
    results = search_vector_store("What is in the document?", vectorstore, k=1)
    print("✅ Retrieved PDF chunk:", results[0].page_content[:100] + "...")
    return results

def test_structured_retrieval():
    print("\n🔍 Testing Structured (SQL) Retrieval...")
    schema_info = load_sqlite_schema_and_samples()
    
    nl_query = "Which artist has the most albums?"
    print(f"User query: {nl_query}")
    
    sql = generate_sql_with_gemini(nl_query, schema_info)
    print(f"Generated SQL: {sql}")
    
    if not sql:
        print("⚠️ No SQL generated.")
        return []
        
    try:
        results = execute_sql_safe(sql)
        print("✅ SQL Execution Result:", results)
        return results
    except Exception as e:
        print(f"❌ SQL Error: {e}")
        return []

if __name__ == "__main__":
    print("🧪 Starting Retrieval Tests...\n")
    
    test_unstructured_retrieval()
    test_structured_retrieval()
    
    print("\n🏁 Retrieval tests completed.")