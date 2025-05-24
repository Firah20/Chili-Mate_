import sqlite3

def connect_db():
    return sqlite3.connect("inventory.db")

def create_table():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Membuat tabel jika belum ada
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_barang TEXT NOT NULL,
        nama_barang TEXT NOT NULL,
        stok INTEGER NOT NULL,
        harga REAL NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def get_all_items():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT kode_barang, nama_barang, stok, harga FROM inventaris")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_item(kode_barang, nama_barang, stok, harga):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO inventaris (kode_barang, nama_barang, stok, harga) 
        VALUES (?, ?, ?, ?)
    ''', (kode_barang, nama_barang, stok, harga))
                   
    conn.commit()
    conn.close()
    
def decrease_item_stock(kode_barang, quantity):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE inventaris 
        SET stok = stok - ? 
        WHERE kode_barang = ?
    ''', (quantity, kode_barang))
    conn.commit()
    conn.close()