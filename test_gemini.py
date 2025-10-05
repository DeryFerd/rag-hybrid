# test_gemini.py
import os
from google import genai

# Ambil API key dari env (Codespaces Secret)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah diset di Codespaces Secrets.")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",  # atau "gemini-2.5-flash" jika tersedia
    contents="Apa ibu kota Indonesia?"
)

print("✅ Gemini API berhasil!")
print("Jawaban:", response.text)