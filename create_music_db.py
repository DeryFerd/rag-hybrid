# create_music_db.py
import sqlite3

# Pastikan folder data/sql ada
import os
os.makedirs("data/sql", exist_ok=True)

# Buat koneksi ke database (akan buat file jika belum ada)
conn = sqlite3.connect("data/sql/music.db")
cur = conn.cursor()

# Buat tabel Artist
cur.execute("""
CREATE TABLE IF NOT EXISTS Artist (
    ArtistId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
)
""")

# Buat tabel Album
cur.execute("""
CREATE TABLE IF NOT EXISTS Album (
    AlbumId INTEGER PRIMARY KEY,
    Title TEXT NOT NULL,
    ArtistId INTEGER,
    FOREIGN KEY (ArtistId) REFERENCES Artist(ArtistId)
)
""")

# Masukkan data contoh
cur.executemany("INSERT INTO Artist VALUES (?, ?)", [
    (1, "Iron Maiden"),
    (2, "Metallica"),
    (3, "AC/DC")
])

cur.executemany("INSERT INTO Album VALUES (?, ?, ?)", [
    (1, "The Number of the Beast", 1),
    (2, "Piece of Mind", 1),
    (3, "Master of Puppets", 2),
    (4, "Ride the Lightning", 2),
    (5, "Back in Black", 3)
])

conn.commit()
conn.close()

print("✅ Database SQLite 'music.db' berhasil dibuat di data/sql/")