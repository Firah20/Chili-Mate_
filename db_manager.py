import sqlite3
import pandas as pd
import db_manager as db
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "inventory.db")

def get_connection():
    return sqlite3.connect(DB_FILE)

DB_PATH = "inventory.db"  # Nama file database SQLite

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    """
    Membuat tabel: items (untuk inventory)
                  journal (untuk Jurnal Umum)
    jika belum ada.
    """
    conn = get_conn()
    c = conn.cursor()
    
def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabel items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            kode TEXT PRIMARY KEY,
            nama TEXT,
            stok INTEGER,
            harga REAL
        )
    """)

    # Tabel jurnal_umum
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jurnal_umum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            akun_debit TEXT,
            akun_kredit TEXT,
            jumlah REAL,
            keterangan TEXT
        )
    """)

    conn.commit()
    conn.close()

def get_all_items():
    """
    Mengambil semua baris dari tabel items.
    Mengembalikan list of tuples: (kode, nama, stok, harga)
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT kode, nama, stok, harga FROM items")
    rows = c.fetchall()
    conn.close()
    return [(r["kode"], r["nama"], r["stok"], r["harga"]) for r in rows]

def add_item(kode, nama, stok, harga):
    """
    Jika barang belum ada (kode baru), insert. 
    Jika sudah ada, update stok dengan menambahkan stok baru, serta update harga.
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT stok FROM items WHERE kode = ?", (kode,))
        existing = c.fetchone()
        if existing:
            new_stok = existing["stok"] + stok
            c.execute("""
                UPDATE items 
                SET nama = ?, stok = ?, harga = ?
                WHERE kode = ?
            """, (nama, new_stok, harga, kode))
        else:
            c.execute("""
                INSERT INTO items (kode, nama, stok, harga)
                VALUES (?, ?, ?, ?)
            """, (kode, nama, stok, harga))
        conn.commit()
        conn.close()
        return True, ""
    except sqlite3.Error as e:
        return False, str(e)

def decrease_item_stock(kode, qty):
    """
    Kurangi stok barang. Jika kode tidak ditemukan atau stok tidak cukup,
    maka return False dengan pesan.
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT stok FROM items WHERE kode = ?", (kode,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "Kode barang tidak ditemukan."
    current = row["stok"]
    if current < qty:
        conn.close()
        return False, f"Stok tidak mencukupi (tersedia: {current})."
    new_stok = current - qty
    c.execute("UPDATE items SET stok = ? WHERE kode = ?", (new_stok, kode))
    conn.commit()
    conn.close()
    return True, ""

def get_all_journal_entries():
    """
    Mengambil semua entri jurnal dari tabel journal, diurutkan dari tanggal asc.
    Mengembalikan list of tuples: (id, tanggal, akun_debit, akun_kredit, jumlah, keterangan)
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, tanggal, akun_debit, akun_kredit, jumlah, keterangan FROM journal ORDER BY tanggal ASC, id ASC")
    rows = c.fetchall()
    conn.close()
    return [(r["id"], r["tanggal"], r["akun_debit"], r["akun_kredit"], r["jumlah"], r["keterangan"]) for r in rows]

def add_journal_entry(tanggal, akun_debit, akun_kredit, jumlah, keterangan):
    """
    Menambahkan entri baru ke tabel journal.
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO journal (tanggal, akun_debit, akun_kredit, jumlah, keterangan)
            VALUES (?, ?, ?, ?, ?)
        """, (tanggal, akun_debit, akun_kredit, jumlah, keterangan))
        conn.commit()
        conn.close()
        return True, ""
    except sqlite3.Error as e:
        return False, str(e)

def create_ledger_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buku_besar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            keterangan TEXT,
            debit REAL,
            kredit REAL
        )
    """)
    conn.commit()
    conn.close()

def get_general_ledger():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT tanggal, keterangan, debit, kredit FROM buku_besar ORDER BY tanggal ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_trial_balance():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ambil total debit per akun
    cursor.execute("""
        SELECT akun_debit AS akun, SUM(jumlah) AS total_debit
        FROM jurnal_umum
        GROUP BY akun_debit
    """)
    debit_rows = cursor.fetchall()
    debit_dict = {akun: jumlah for akun, jumlah in debit_rows}

    # Ambil total kredit per akun
    cursor.execute("""
        SELECT akun_kredit AS akun, SUM(jumlah) AS total_kredit
        FROM jurnal_umum
        GROUP BY akun_kredit
    """)
    kredit_rows = cursor.fetchall()
    kredit_dict = {akun: jumlah for akun, jumlah in kredit_rows}

    akun_set = set(debit_dict.keys()) | set(kredit_dict.keys())
    trial_balance = []
    for akun in sorted(akun_set):
        total_debit = debit_dict.get(akun, 0)
        total_kredit = kredit_dict.get(akun, 0)
        trial_balance.append((akun, total_debit, total_kredit))

    conn.close()
    return trial_balance

def get_trial_balance():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ambil total debit per akun
    cursor.execute("""
        SELECT akun_debit AS akun, SUM(jumlah) AS total_debit
        FROM jurnal_umum
        GROUP BY akun_debit
    """)
    debit_rows = cursor.fetchall()
    debit_dict = {akun: jumlah for akun, jumlah in debit_rows}

    # Ambil total kredit per akun
    cursor.execute("""
        SELECT akun_kredit AS akun, SUM(jumlah) AS total_kredit
        FROM jurnal_umum
        GROUP BY akun_kredit
    """)
    kredit_rows = cursor.fetchall()
    kredit_dict = {akun: jumlah for akun, jumlah in kredit_rows}

    akun_set = set(debit_dict.keys()) | set(kredit_dict.keys())
    trial_balance = []
    for akun in sorted(akun_set):
        total_debit = debit_dict.get(akun, 0)
        total_kredit = kredit_dict.get(akun, 0)
        trial_balance.append((akun, total_debit, total_kredit))

    conn.close()
    return trial_balance

