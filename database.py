import sqlite3


def setup_db():
    conn = sqlite3.connect("peminjaman_buku.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daftar_buku (
            id_buku INTEGER PRIMARY KEY AUTOINCREMENT,
            judul_buku TEXT,
            penulis TEXT,
            penerbit TEXT,
            kategori TEXT,
            stok_buku INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daftar_anggota (
            id_anggota INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_anggota TEXT,
            nomor_hp TEXT,
            alamat TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS peminjaman_buku (
            id_peminjaman INTEGER PRIMARY KEY AUTOINCREMENT,
            peminjam INTEGER,
            tanggal_pinjam DATE,
            tanggal_kembali DATE,
            jumlah_buku_yang_dipinjam INTEGER,
            judul_buku_id INTEGER,
            FOREIGN KEY (peminjam) REFERENCES daftar_anggota (id_anggota)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (judul_buku_id) REFERENCES daftar_buku (id_buku)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """)

    conn.commit()
    conn.close()
