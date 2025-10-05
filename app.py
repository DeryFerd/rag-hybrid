# app.py
import gradio as gr
from src.ingest.pdf_loader import load_and_chunk_pdfs
from src.ingest.sql_loader import load_sqlite_schema_and_samples
from src.retrieval.vector_store import load_or_create_vector_store, search_vector_store
from src.retrieval.sql_retriever import generate_sql_with_gemini, execute_sql_safe
from src.agents.hybrid_rag_agent import hybrid_rag_answer

# Load resources once at startup
print("🚀 Initializing Hybrid RAG system...")
PDF_CHUNKS = load_and_chunk_pdfs()
VECTORSTORE = load_or_create_vector_store(PDF_CHUNKS)
SCHEMA_INFO = load_sqlite_schema_and_samples()
print("✅ System ready!")

def chatbot_response(user_query: str) -> tuple[str, str]:
    """
    Main chatbot function for Gradio.
    Returns (answer, debug_info)
    """
    try:
        # Unstructured retrieval
        retrieved_docs = search_vector_store(user_query, VECTORSTORE, k=2)
        
        # Structured retrieval
        generated_sql = ""
        sql_result = []
        try:
            generated_sql = generate_sql_with_gemini(user_query, SCHEMA_INFO)
            if generated_sql:
                sql_result = execute_sql_safe(generated_sql)
        except Exception as e:
            print(f"⚠️ SQL error: {e}")
            generated_sql = ""
            sql_result = []

        # Generate final answer
        final_answer = hybrid_rag_answer(
            user_query=user_query,
            pdf_chunks=retrieved_docs,
            sql_result=sql_result,
            generated_sql=generated_sql
        )

        # Build debug/provenance info
        debug_info = "## Provenance\n"
        if generated_sql:
            debug_info += f"**SQL Used:**\n```sql\n{generated_sql}\n```\n\n"
        else:
            debug_info += "No SQL query generated.\n\n"
        
        if retrieved_docs:
            doc_texts = [doc.page_content.strip() for doc in retrieved_docs if doc.page_content.strip()]
            if doc_texts:
                debug_info += "**Retrieved Document Snippets:**\n" + "\n".join(f"- {t}" for t in doc_texts[:2])
            else:
                debug_info += "No relevant document snippets found."
        else:
            debug_info += "No relevant document snippets found."

        return final_answer, debug_info

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return error_msg, error_msg

# Gradio Interface
with gr.Blocks(title="Hybrid RAG Chatbot") as demo:
    gr.Markdown("## 🎵 Hybrid RAG Chatbot (PDF + SQL)")
    gr.Markdown("Ask questions about music artists, albums, or anything in the documents!")
    
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label="Your question", placeholder="e.g., Which artist has the most albums?")
    clear = gr.ClearButton([msg, chatbot])
    
    with gr.Accordion("🔍 Provenance & Debug Info", open=False):
        debug_output = gr.Markdown()

    def respond(message, chat_history):
        bot_message, debug_info = chatbot_response(message)
        chat_history.append((message, bot_message))
        return "", chat_history, debug_info

    msg.submit(respond, [msg, chatbot], [msg, chatbot, debug_output])
    clear.click(lambda: ([], ""), None, [chatbot, debug_output])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)