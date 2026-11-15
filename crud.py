import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

COLOR_BG = "#F4F6F8"
COLOR_CARD = "#FFFFFF"
COLOR_HEADER = "#2C3E50"
COLOR_TEXT = "#333333"
COLOR_PRIMARY = "#7393B3"
COLOR_SUCCESS = "#8FBC8F"
COLOR_WARNING = "#E9967A"
COLOR_DANGER = "#E57373"
COLOR_NEUTRAL = "#A0AAB2"


# --- 1. SETUP DATABASE ---
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


# --- 2. FUNGSI PINDAH HALAMAN ---
def buka_halaman(halaman):
    halaman_menu.pack_forget()
    halaman_daftar_buku.pack_forget()
    halaman_daftar_anggota.pack_forget()
    halaman_pengembalian.pack_forget()

    halaman.pack(fill="both", expand=True)

    if halaman == halaman_daftar_buku:
        muat_data_buku()
        reset_form_buku()

    if halaman == halaman_daftar_anggota:
        muat_data_anggota()
        reset_form_anggota()

    if halaman == halaman_pengembalian:
        muat_data_peminjaman()
        muat_pilihan_peminjaman()
        reset_form_peminjaman()


# --- 3. FUNGSI CRUD & FORM DAFTAR BUKU ---
def muat_data_buku():
    for row in tabel_daftar_buku.get_children():
        tabel_daftar_buku.delete(row)

    conn = sqlite3.connect("peminjaman_buku.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daftar_buku")
    for row in cursor.fetchall():
        tabel_daftar_buku.insert("", tk.END, values=row)
    conn.close()


def tambah_data_buku():
    judul_buku = entry_judul.get()
    penulis = entry_penulis.get()
    penerbit = entry_penerbit.get()
    kategori = entry_kategori.get()
    stok_buku = entry_stok.get()

    if not judul_buku or not penulis or not penerbit or not kategori or not stok_buku:
        messagebox.showerror("Error", "Semua kolom harus diisi!")
        return

    try:
        stok_buku = int(stok_buku)
        if stok_buku < 0:
            messagebox.showerror("Error", "Stok tidak boleh kurang dari 0!")
            return

        conn = sqlite3.connect("peminjaman_buku.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO daftar_buku
            (judul_buku, penulis, penerbit, kategori, stok_buku)
            VALUES (?, ?, ?, ?, ?)
        """,
            (judul_buku, penulis, penerbit, kategori, stok_buku),
        )
        conn.commit()
        conn.close()

        muat_data_buku()
        reset_form_buku()
        messagebox.showinfo("Sukses", "Data berhasil disimpan!")

    except ValueError:
        messagebox.showerror("Error", "Kolom Stok Buku harus berupa angka!")


def pilih_data_buku(event):
    global selected_book
    try:
        selected_item = tabel_daftar_buku.selection()[0]
        values = tabel_daftar_buku.item(selected_item, "values")
        selected_book = values[0]

        entry_judul.delete(0, tk.END)
        entry_judul.insert(0, values[1])
        entry_penulis.delete(0, tk.END)
        entry_penulis.insert(0, values[2])
        entry_penerbit.delete(0, tk.END)
        entry_penerbit.insert(0, values[3])
        entry_kategori.delete(0, tk.END)
        entry_kategori.insert(0, values[4])
        entry_stok.delete(0, tk.END)
        entry_stok.insert(0, values[5])
    except IndexError:
        pass


def update_data_buku():
    if not selected_book:
        messagebox.showerror("Error", "Pilih dulu data dari tabel yang mau diubah!")
        return

    judul_buku = entry_judul.get()
    penulis = entry_penulis.get()
    penerbit = entry_penerbit.get()
    kategori = entry_kategori.get()
    stok_buku = entry_stok.get()

    if not judul_buku or not penulis or not penerbit or not kategori or not stok_buku:
        messagebox.showerror("Error", "Semua kolom harus diisi!")
        return

    try:
        stok_buku = int(stok_buku)
        if stok_buku < 0:
            messagebox.showerror("Error", "Stok tidak boleh kurang dari 0!")
            return

        conn = sqlite3.connect("peminjaman_buku.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE daftar_buku
            SET judul_buku = ?, penulis = ?, penerbit = ?, kategori = ?, stok_buku = ?
            WHERE id_buku = ?
        """,
            (judul_buku, penulis, penerbit, kategori, stok_buku, selected_book),
        )
        conn.commit()
        conn.close()

        muat_data_buku()
        reset_form_buku()
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")

    except ValueError:
        messagebox.showerror("Error", "Kolom Stok Buku harus berupa angka!")


def hapus_data_buku():
    if not selected_book:
        messagebox.showerror("Error", "Pilih dulu data yang mau dihapus!")
        return

    if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
        conn = sqlite3.connect("peminjaman_buku.db")
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daftar_buku WHERE id_buku = ?", (selected_book,))
        conn.commit()
        conn.close()

        muat_data_buku()
        reset_form_buku()
        messagebox.showinfo("Sukses", "Data berhasil dihapus!")


def reset_form_buku():
    global selected_book
    selected_book = None
    entry_judul.delete(0, tk.END)
    entry_penulis.delete(0, tk.END)
    entry_penerbit.delete(0, tk.END)
    entry_kategori.delete(0, tk.END)
    entry_stok.delete(0, tk.END)


# --- 4. FUNGSI CRUD & FORM DAFTAR ANGGOTA ---
def muat_data_anggota():
    for row in tabel_daftar_anggota.get_children():
        tabel_daftar_anggota.delete(row)

    conn = sqlite3.connect("peminjaman_buku.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daftar_anggota")
    for row in cursor.fetchall():
        tabel_daftar_anggota.insert("", tk.END, values=row)
    conn.close()


def tambah_data_anggota():
    nama = entry_nama_anggota.get()
    nomor_hp = entry_nomor_hp.get()
    alamat = entry_alamat_anggota.get()

    if not nama or not nomor_hp or not alamat:
        messagebox.showerror("Error", "Semua kolom harus diisi!")
        return

    conn = sqlite3.connect("peminjaman_buku.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO daftar_anggota (nama_anggota, nomor_hp, alamat)
        VALUES (?, ?, ?)
    """,
        (nama, nomor_hp, alamat),
    )
    conn.commit()
    conn.close()

    muat_data_anggota()
    reset_form_anggota()
    messagebox.showinfo("Sukses", "Data anggota berhasil disimpan!")


def pilih_data_anggota(event):
    global selected_member
    try:
        selected_item = tabel_daftar_anggota.selection()[0]
        values = tabel_daftar_anggota.item(selected_item, "values")
        selected_member = values[0]

        entry_nama_anggota.delete(0, tk.END)
        entry_nama_anggota.insert(0, values[1])
        entry_nomor_hp.delete(0, tk.END)
        entry_nomor_hp.insert(0, values[2])
        entry_alamat_anggota.delete(0, tk.END)
        entry_alamat_anggota.insert(0, values[3])
    except IndexError:
        pass


def update_data_anggota():
    if not selected_member:
        messagebox.showerror("Error", "Pilih dulu data dari tabel yang mau diubah!")
        return

    nama = entry_nama_anggota.get()
    nomor_hp = entry_nomor_hp.get()
    alamat = entry_alamat_anggota.get()

    if not nama or not nomor_hp or not alamat:
        messagebox.showerror("Error", "Semua kolom harus diisi!")
        return

    conn = sqlite3.connect("peminjaman_buku.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE daftar_anggota
        SET nama_anggota = ?, nomor_hp = ?, alamat = ?
        WHERE id_anggota = ?
    """,
        (nama, nomor_hp, alamat, selected_member),
    )
    conn.commit()
    conn.close()

    muat_data_anggota()
    reset_form_anggota()
    messagebox.showinfo("Sukses", "Data anggota berhasil diperbarui!")


def hapus_data_anggota():
    if not selected_member:
        messagebox.showerror("Error", "Pilih dulu data yang mau dihapus!")
        return

    if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
        conn = sqlite3.connect("peminjaman_buku.db")
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM daftar_anggota WHERE id_anggota = ?", (selected_member,)
        )
        conn.commit()
        conn.close()

        muat_data_anggota()
        reset_form_anggota()
        messagebox.showinfo("Sukses", "Data anggota berhasil dihapus!")


def reset_form_anggota():
    global selected_member
    selected_member = None
    entry_nama_anggota.delete(0, tk.END)
    entry_nomor_hp.delete(0, tk.END)
    entry_alamat_anggota.delete(0, tk.END)


# --- 5. FUNGSI PEMINJAMAN & PENGEMBALIAN ---
def muat_pilihan_peminjaman():
    conn = sqlite3.connect("peminjaman_buku.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id_anggota, nama_anggota FROM daftar_anggota")
    anggota = cursor.fetchall()
    pilihan_anggota["values"] = [f"{row[0]} - {row[1]}" for row in anggota]

    cursor.execute("SELECT id_buku, judul_buku, stok_buku FROM daftar_buku")
    buku = cursor.fetchall()
    pilihan_buku["values"] = [f"{row[0]} - {row[1]} (stok: {row[2]})" for row in buku]
    conn.close()


def muat_data_peminjaman():
    for row in tabel_peminjaman.get_children():
        tabel_peminjaman.delete(row)

    conn = sqlite3.connect("peminjaman_buku.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT peminjaman_buku.id_peminjaman,
               daftar_anggota.nama_anggota,
               daftar_buku.judul_buku,
               peminjaman_buku.jumlah_buku_yang_dipinjam,
               peminjaman_buku.tanggal_pinjam,
               peminjaman_buku.tanggal_kembali
        FROM peminjaman_buku
        JOIN daftar_anggota ON peminjaman_buku.peminjam = daftar_anggota.id_anggota
        JOIN daftar_buku ON peminjaman_buku.judul_buku_id = daftar_buku.id_buku
        ORDER BY peminjaman_buku.id_peminjaman DESC
    """)
    for row in cursor.fetchall():
        tabel_peminjaman.insert("", tk.END, values=row)
    conn.close()


def reset_form_peminjaman():
    pilihan_anggota.set("")
    pilihan_buku.set("")
    entry_jumlah_pinjam.delete(0, tk.END)


def tambah_data_peminjaman():
    anggota = pilihan_anggota.get()
    buku = pilihan_buku.get()
    jumlah = entry_jumlah_pinjam.get()

    if not anggota or not buku or not jumlah:
        messagebox.showerror("Error", "Pilih anggota, buku, dan isi jumlah buku!")
        return

    try:
        jumlah = int(jumlah)
        if jumlah <= 0:
            messagebox.showerror("Error", "Jumlah buku harus lebih dari 0!")
            return

        id_anggota = int(anggota.split(" - ")[0])
        id_buku = int(buku.split(" - ")[0])

        conn = sqlite3.connect("peminjaman_buku.db")
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT stok_buku FROM daftar_buku WHERE id_buku = ?", (id_buku,)
        )
        hasil = cursor.fetchone()

        if hasil is None:
            messagebox.showerror("Error", "Buku tidak ditemukan!")
            conn.close()
            return

        if jumlah > hasil[0]:
            messagebox.showerror("Error", "Stok buku tidak mencukupi!")
            conn.close()
            return

        cursor.execute(
            """
            INSERT INTO peminjaman_buku
            (peminjam, tanggal_pinjam, tanggal_kembali,
             jumlah_buku_yang_dipinjam, judul_buku_id)
            VALUES (?, DATE('now', 'localtime'), NULL, ?, ?)
        """,
            (id_anggota, jumlah, id_buku),
        )

        cursor.execute(
            """
            UPDATE daftar_buku
            SET stok_buku = stok_buku - ?
            WHERE id_buku = ?
        """,
            (jumlah, id_buku),
        )

        conn.commit()
        conn.close()

        muat_data_peminjaman()
        muat_pilihan_peminjaman()
        entry_jumlah_pinjam.delete(0, tk.END)
        pilihan_anggota.set("")
        pilihan_buku.set("")
        messagebox.showinfo("Sukses", "Peminjaman buku berhasil dicatat!")

    except ValueError:
        messagebox.showerror("Error", "Jumlah buku tidak valid!")


def kembalikan_data_buku():
    try:
        selected_item = tabel_peminjaman.selection()[0]
        values = tabel_peminjaman.item(selected_item, "values")
        id_peminjaman = values[0]
    except IndexError:
        messagebox.showerror("Error", "Pilih transaksi yang ingin dikembalikan!")
        return

    conn = sqlite3.connect("peminjaman_buku.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT judul_buku_id, jumlah_buku_yang_dipinjam, tanggal_kembali
        FROM peminjaman_buku
        WHERE id_peminjaman = ?
    """,
        (id_peminjaman,),
    )
    data = cursor.fetchone()

    if data is None:
        conn.close()
        messagebox.showerror("Error", "Transaksi tidak ditemukan!")
        return

    id_buku, jumlah, tanggal_kembali = data

    if tanggal_kembali is not None:
        conn.close()
        messagebox.showinfo("Informasi", "Buku ini sudah dikembalikan sebelumnya!")
        return

    cursor.execute(
        """
        UPDATE peminjaman_buku
        SET tanggal_kembali = DATE('now', 'localtime')
        WHERE id_peminjaman = ?
    """,
        (id_peminjaman,),
    )

    cursor.execute(
        """
        UPDATE daftar_buku
        SET stok_buku = stok_buku + ?
        WHERE id_buku = ?
    """,
        (jumlah, id_buku),
    )

    conn.commit()
    conn.close()

    muat_data_peminjaman()
    muat_pilihan_peminjaman()
    messagebox.showinfo(
        "Sukses", "Buku berhasil dikembalikan dan stok telah ditambahkan!"
    )


# --- 6. MEMBUAT WINDOW ---
window = tk.Tk()
window.title("Aplikasi Peminjaman Buku")
window.geometry("850x650")
window.configure(bg=COLOR_BG)

selected_book = None
selected_member = None

# ==========================================
# HALAMAN 1: MENU UTAMA (Dashboard Card Style)
# ==========================================
halaman_menu = tk.Frame(window, bg=COLOR_BG)

card_menu = tk.Frame(halaman_menu, bg=COLOR_CARD, bd=1, relief="solid")
card_menu.pack(expand=True, fill="both", padx=40, pady=40)

tk.Label(
    card_menu,
    text="📖 PUSTAKA DIGITAL",
    font=("Segoe UI", 24, "bold"),
    bg=COLOR_CARD,
    fg=COLOR_HEADER,
).pack(pady=(40, 10))

tk.Label(
    card_menu,
    text="Sistem Pengelolaan Data & Transaksi Peminjaman Buku",
    font=("Segoe UI", 12),
    bg=COLOR_CARD,
    fg=COLOR_NEUTRAL,
).pack(pady=(0, 40))

tk.Button(
    card_menu,
    text="📖 Kelola Data Buku",
    font=("Segoe UI", 12, "bold"),
    bg=COLOR_PRIMARY,
    fg="white",
    activebackground="#5C7893",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    pady=10,
    command=lambda: buka_halaman(halaman_daftar_buku),
).pack(pady=12, padx=120, fill="x")

tk.Button(
    card_menu,
    text="👤 Kelola Data Anggota",
    font=("Segoe UI", 12, "bold"),
    bg=COLOR_PRIMARY,
    fg="white",
    activebackground="#5C7893",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    pady=10,
    command=lambda: buka_halaman(halaman_daftar_anggota),
).pack(pady=12, padx=120, fill="x")

tk.Button(
    card_menu,
    text="🔄 Peminjaman & Pengembalian",
    font=("Segoe UI", 12, "bold"),
    bg=COLOR_SUCCESS,
    fg="white",
    activebackground="#769C76",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    pady=10,
    command=lambda: buka_halaman(halaman_pengembalian),
).pack(pady=12, padx=120, fill="x")


# ==========================================
# HALAMAN 2: DAFTAR BUKU CRUD
# ==========================================
halaman_daftar_buku = tk.Frame(window, bg=COLOR_BG)

# Navigasi Top Bar
top_bar_buku = tk.Frame(halaman_daftar_buku, bg=COLOR_BG)
top_bar_buku.pack(fill="x", pady=(10, 10), padx=10)

tk.Button(
    top_bar_buku,
    text="← Kembali",
    width=12,
    bg=COLOR_NEUTRAL,
    fg="white",
    activebackground="#88939C",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=lambda: buka_halaman(halaman_menu),
).pack(side="left")

tk.Label(
    top_bar_buku,
    text="PENGELOLAAN DATA BUKU",
    font=("Segoe UI", 16, "bold"),
    bg=COLOR_BG,
    fg=COLOR_HEADER,
).pack(side="left", padx=20)

# Form Input Card
card_form_buku = tk.Frame(halaman_daftar_buku, bg=COLOR_CARD, bd=1, relief="solid")
card_form_buku.pack(fill="x", pady=10, padx=10)

grid_buku = tk.Frame(card_form_buku, bg=COLOR_CARD)
grid_buku.pack(pady=15, padx=20, fill="x")

# Column 1
tk.Label(
    grid_buku, text="Judul Buku:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)
).grid(row=0, column=0, sticky="w", pady=6)
entry_judul = tk.Entry(grid_buku, width=28, font=("Segoe UI", 10))
entry_judul.grid(row=0, column=1, padx=(5, 20), pady=6)

tk.Label(
    grid_buku, text="Penulis:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)
).grid(row=1, column=0, sticky="w", pady=6)
entry_penulis = tk.Entry(grid_buku, width=28, font=("Segoe UI", 10))
entry_penulis.grid(row=1, column=1, padx=(5, 20), pady=6)

tk.Label(
    grid_buku, text="Penerbit:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)
).grid(row=2, column=0, sticky="w", pady=6)
entry_penerbit = tk.Entry(grid_buku, width=28, font=("Segoe UI", 10))
entry_penerbit.grid(row=2, column=1, padx=(5, 20), pady=6)

# Column 2
tk.Label(
    grid_buku, text="Kategori:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)
).grid(row=0, column=2, sticky="w", pady=6)
entry_kategori = tk.Entry(grid_buku, width=28, font=("Segoe UI", 10))
entry_kategori.grid(row=0, column=3, padx=5, pady=6)

tk.Label(
    grid_buku, text="Stok Buku:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)
).grid(row=1, column=2, sticky="w", pady=6)
entry_stok = tk.Entry(grid_buku, width=28, font=("Segoe UI", 10))
entry_stok.grid(row=1, column=3, padx=5, pady=6)

# Button Panel
frame_btn_buku = tk.Frame(halaman_daftar_buku, bg=COLOR_BG)
frame_btn_buku.pack(pady=5)

tk.Button(
    frame_btn_buku,
    text="+ Tambah",
    bg=COLOR_SUCCESS,
    fg="white",
    activebackground="#769C76",
    activeforeground="white",
    width=12,
    relief="flat",
    cursor="hand2",
    command=tambah_data_buku,
).pack(side="left", padx=5)
tk.Button(
    frame_btn_buku,
    text="✏️ Update",
    bg=COLOR_WARNING,
    fg="white",
    activebackground="#D88266",
    activeforeground="white",
    width=12,
    relief="flat",
    cursor="hand2",
    command=update_data_buku,
).pack(side="left", padx=5)
tk.Button(
    frame_btn_buku,
    text="🗑️ Hapus",
    bg=COLOR_DANGER,
    fg="white",
    activebackground="#CE5C5C",
    activeforeground="white",
    width=12,
    relief="flat",
    cursor="hand2",
    command=hapus_data_buku,
).pack(side="left", padx=5)
tk.Button(
    frame_btn_buku,
    text="🔄 Reset",
    bg=COLOR_NEUTRAL,
    fg="white",
    activebackground="#88939C",
    activeforeground="white",
    width=12,
    relief="flat",
    cursor="hand2",
    command=reset_form_buku,
).pack(side="left", padx=5)

# Treeview Table
columns_buku = ("ID Buku", "Judul Buku", "Penulis", "Penerbit", "Kategori", "Stok")
tabel_daftar_buku = ttk.Treeview(
    halaman_daftar_buku, columns=columns_buku, show="headings", height=9
)

for col in columns_buku:
    tabel_daftar_buku.heading(col, text=col)
    tabel_daftar_buku.column(col, width=130, anchor="center")

tabel_daftar_buku.pack(padx=10, pady=10, fill="both", expand=True)
tabel_daftar_buku.bind("<ButtonRelease-1>", pilih_data_buku)


# ==========================================
# HALAMAN 3: DAFTAR ANGGOTA CRUD
# ==========================================
halaman_daftar_anggota = tk.Frame(window, bg=COLOR_BG)

top_bar_anggota = tk.Frame(halaman_daftar_anggota, bg=COLOR_BG)
top_bar_anggota.pack(fill="x", pady=(10, 10), padx=10)

tk.Button(
    top_bar_anggota,
    text="← Kembali",
    width=12,
    bg=COLOR_NEUTRAL,
    fg="white",
    activebackground="#88939C",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=lambda: buka_halaman(halaman_menu),
).pack(side="left")

tk.Label(
    top_bar_anggota,
    text="PENGELOLAAN DATA ANGGOTA",
    font=("Segoe UI", 16, "bold"),
    bg=COLOR_BG,
    fg=COLOR_HEADER,
).pack(side="left", padx=20)

card_form_anggota = tk.Frame(
    halaman_daftar_anggota, bg=COLOR_CARD, bd=1, relief="solid"
)
card_form_anggota.pack(fill="x", pady=10, padx=10)

grid_anggota = tk.Frame(card_form_anggota, bg=COLOR_CARD)
grid_anggota.pack(pady=15, padx=20)

tk.Label(
    grid_anggota,
    text="Nama Anggota:",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10),
).grid(row=0, column=0, sticky="w", pady=6)
entry_nama_anggota = tk.Entry(grid_anggota, width=38, font=("Segoe UI", 10))
entry_nama_anggota.grid(row=0, column=1, padx=10, pady=6)

tk.Label(
    grid_anggota, text="Nomor HP:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)
).grid(row=1, column=0, sticky="w", pady=6)
entry_nomor_hp = tk.Entry(grid_anggota, width=38, font=("Segoe UI", 10))
entry_nomor_hp.grid(row=1, column=1, padx=10, pady=6)

tk.Label(
    grid_anggota, text="Alamat:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)
).grid(row=2, column=0, sticky="w", pady=6)
entry_alamat_anggota = tk.Entry(grid_anggota, width=38, font=("Segoe UI", 10))
entry_alamat_anggota.grid(row=2, column=1, padx=10, pady=6)

frame_btn_anggota = tk.Frame(halaman_daftar_anggota, bg=COLOR_BG)
frame_btn_anggota.pack(pady=5)

tk.Button(
    frame_btn_anggota,
    text="+ Tambah",
    bg=COLOR_SUCCESS,
    fg="white",
    activebackground="#769C76",
    activeforeground="white",
    width=12,
    relief="flat",
    cursor="hand2",
    command=tambah_data_anggota,
).pack(side="left", padx=5)
tk.Button(
    frame_btn_anggota,
    text="✏️ Update",
    bg=COLOR_WARNING,
    fg="white",
    activebackground="#D88266",
    activeforeground="white",
    width=12,
    relief="flat",
    cursor="hand2",
    command=update_data_anggota,
).pack(side="left", padx=5)
tk.Button(
    frame_btn_anggota,
    text="🗑️ Hapus",
    bg=COLOR_DANGER,
    fg="white",
    activebackground="#CE5C5C",
    activeforeground="white",
    width=12,
    relief="flat",
    cursor="hand2",
    command=hapus_data_anggota,
).pack(side="left", padx=5)
tk.Button(
    frame_btn_anggota,
    text="🔄 Reset",
    bg=COLOR_NEUTRAL,
    fg="white",
    activebackground="#88939C",
    activeforeground="white",
    width=12,
    relief="flat",
    cursor="hand2",
    command=reset_form_anggota,
).pack(side="left", padx=5)

columns_anggota = ("ID Anggota", "Nama Anggota", "Nomor HP", "Alamat")
tabel_daftar_anggota = ttk.Treeview(
    halaman_daftar_anggota, columns=columns_anggota, show="headings", height=9
)

for col in columns_anggota:
    tabel_daftar_anggota.heading(col, text=col)
    tabel_daftar_anggota.column(col, width=180, anchor="center")

tabel_daftar_anggota.pack(padx=10, pady=10, fill="both", expand=True)
tabel_daftar_anggota.bind("<ButtonRelease-1>", pilih_data_anggota)


# ==========================================
# HALAMAN 4: PEMINJAMAN & PENGEMBALIAN
# ==========================================
halaman_pengembalian = tk.Frame(window, bg=COLOR_BG)

top_bar_pinjam = tk.Frame(halaman_pengembalian, bg=COLOR_BG)
top_bar_pinjam.pack(fill="x", pady=(10, 10), padx=10)

tk.Button(
    top_bar_pinjam,
    text="← Kembali",
    width=12,
    bg=COLOR_NEUTRAL,
    fg="white",
    activebackground="#88939C",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=lambda: buka_halaman(halaman_menu),
).pack(side="left")

tk.Label(
    top_bar_pinjam,
    text="PEMINJAMAN & PENGEMBALIAN BUKU",
    font=("Segoe UI", 16, "bold"),
    bg=COLOR_BG,
    fg=COLOR_HEADER,
).pack(side="left", padx=20)

card_form_pinjam = tk.Frame(halaman_pengembalian, bg=COLOR_CARD, bd=1, relief="solid")
card_form_pinjam.pack(fill="x", pady=10, padx=10)

grid_pinjam = tk.Frame(card_form_pinjam, bg=COLOR_CARD)
grid_pinjam.pack(pady=15, padx=20)

tk.Label(
    grid_pinjam,
    text="Pilih Anggota:",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10),
).grid(row=0, column=0, sticky="w", pady=6)
pilihan_anggota = ttk.Combobox(
    grid_pinjam, width=38, state="readonly", font=("Segoe UI", 10)
)
pilihan_anggota.grid(row=0, column=1, padx=10, pady=6)

tk.Label(
    grid_pinjam, text="Pilih Buku:", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)
).grid(row=1, column=0, sticky="w", pady=6)
pilihan_buku = ttk.Combobox(
    grid_pinjam, width=38, state="readonly", font=("Segoe UI", 10)
)
pilihan_buku.grid(row=1, column=1, padx=10, pady=6)

tk.Label(
    grid_pinjam,
    text="Jumlah Buku:",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10),
).grid(row=2, column=0, sticky="w", pady=6)
entry_jumlah_pinjam = tk.Entry(grid_pinjam, width=41, font=("Segoe UI", 10))
entry_jumlah_pinjam.grid(row=2, column=1, padx=10, pady=6)

tk.Button(
    card_form_pinjam,
    text="➕ Catat Peminjaman",
    bg=COLOR_SUCCESS,
    fg="white",
    activebackground="#769C76",
    activeforeground="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    cursor="hand2",
    pady=5,
    command=tambah_data_peminjaman,
).pack(pady=(0, 15))

columns_peminjaman = (
    "ID Transaksi",
    "Nama Anggota",
    "Judul Buku",
    "Jumlah",
    "Tgl Pinjam",
    "Tgl Kembali",
)
tabel_peminjaman = ttk.Treeview(
    halaman_pengembalian, columns=columns_peminjaman, show="headings", height=8
)

for col in columns_peminjaman:
    tabel_peminjaman.heading(col, text=col)
    tabel_peminjaman.column(col, width=130, anchor="center")

tabel_peminjaman.pack(padx=10, pady=5, fill="both", expand=True)

tk.Button(
    halaman_pengembalian,
    text="↩️ Kembalikan Buku (Selesai Pinjam)",
    bg=COLOR_PRIMARY,
    fg="white",
    activebackground="#5C7893",
    activeforeground="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    cursor="hand2",
    pady=8,
    command=kembalikan_data_buku,
).pack(pady=10)


# --- 7. MENJALANKAN APLIKASI ---
setup_db()
buka_halaman(halaman_menu)
window.mainloop()
