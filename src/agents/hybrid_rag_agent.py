# src/agents/hybrid_rag_agent.py
import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from google import genai

def summarize_sql_result(sql_result: List[Dict]) -> str:
    """
    Convert SQL result (list of dicts) into a natural language summary.
    Example: [{'Name': 'Metallica'}] → "The artist with the most albums is Metallica."
    """
    if not sql_result:
        return "No data found in the database."
    
    # Simple heuristic: if single row + single column
    if len(sql_result) == 1 and len(sql_result[0]) == 1:
        value = list(sql_result[0].values())[0]
        return f"The result is: {value}."
    
    # General case: describe as table
    lines = ["Database returned the following records:"]
    for row in sql_result:
        lines.append(" - " + ", ".join(f"{k}: {v}" for k, v in row.items()))
    return "\n".join(lines)

def format_retrieved_context(
    pdf_chunks: List[Document],
    sql_result: List[Dict],
    generated_sql: str = ""
) -> str:
    """
    Format both unstructured and structured context for the LLM.
    """
    context_parts = []

    # Unstructured context
    if pdf_chunks:
        pdf_texts = [doc.page_content.strip() for doc in pdf_chunks if doc.page_content.strip()]
        if pdf_texts:
            context_parts.append("## Unstructured Context (from documents):\n" + "\n".join(f"- {t}" for t in pdf_texts))

    # Structured context
    if sql_result:
        sql_summary = summarize_sql_result(sql_result)
        context_parts.append("## Structured Context (from database):\n" + sql_summary)
        if generated_sql:
            context_parts.append(f"**SQL used:**\n```sql\n{generated_sql}\n```")

    return "\n\n".join(context_parts) if context_parts else "No relevant context found."

def hybrid_rag_answer(
    user_query: str,
    pdf_chunks: List[Document],
    sql_result: List[Dict],
    generated_sql: str = ""
) -> str:
    """
    Generate final answer using Gemini, combining both structured and unstructured context.
    """
    context = format_retrieved_context(pdf_chunks, sql_result, generated_sql)
    
    prompt = f"""You are an intelligent assistant that answers questions using both document knowledge and live database results.

User question: {user_query}

{context}

Instructions:
- Answer concisely and truthfully.
- If data comes from the database, mention it (e.g., "According to the database...").
- If info comes from documents, cite it (e.g., "The document states...").
- If both sources are present, synthesize them logically.
- Do not hallucinate. If unsure, say "I don't know".
- Include the SQL query if it was used.

Final answer:"""

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()