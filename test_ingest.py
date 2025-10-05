# test_ingest.py
from src.ingest.pdf_loader import load_and_chunk_pdfs
from src.ingest.sql_loader import load_sqlite_schema_and_samples

if __name__ == "__main__":
    # PDF
    pdf_chunks = load_and_chunk_pdfs()
    if pdf_chunks:
        print("Sample PDF chunk:", pdf_chunks[0].page_content[:200])

    # SQL
    db_info = load_sqlite_schema_and_samples()
    for table, info in db_info.items():
        print(f"\nTable: {table}")
        print("Schema:", info["schema"])
        print("Sample:", info["sample_rows"])