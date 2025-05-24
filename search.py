# search.py

import sqlite3

def search_items(keyword):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT kode_barang, nama_barang, stok, harga FROM inventaris 
                      WHERE kode_barang LIKE ? OR nama_barang LIKE ?''', 
                    (f"%{keyword}%", f"%{keyword}%"))  
    rows = cursor.fetchall()
    conn.close() 
    return rows