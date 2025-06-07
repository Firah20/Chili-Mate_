import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime
from products import products
from db_manager import add_item, get_all_items, decrease_item_stock, create_table, get_all_journal_entries, add_journal_entry
from checkout import show_checkout_form
import os
import sqlite3 

# AUTHENTICATION SYSTEM
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password, stored_hash):
    return hash_password(input_password) == stored_hash

def init_user_database():
    """Initialize the user database in session state"""
    if "users_db" not in st.session_state:
        st.session_state.users_db = {
            "admin": {
                "password_hash": hash_password("admin123"),
                "role": "admin",
                "email": "admin@chilimate.com"
            },
            "staff": {
                "password_hash": hash_password("staff123"),
                "role": "staff",
                "email": "staff@chilimate.com"
            },
            "customer": {
                "password_hash": hash_password("customer123"),
                "role": "customer",
                "email": "customer@chilimate.com"
            }
        }

def authenticate(username, password):
    """Authenticate a user and return user data if successful"""
    if username in st.session_state.users_db:
        user_data = st.session_state.users_db[username]
        if verify_password(password, user_data["password_hash"]):
            return {
                "authenticated": True,
                "username": username,
                "role": user_data["role"],
                "email": user_data.get("email", "")
            }
    return {
        "authenticated": False,
        "username": None,
        "role": None,
        "email": None
    }
def register_user(username, password, email=None, role="customer"):
    """Register a new user"""
    if username in st.session_state.users_db:
        return False, "Username already exists"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    st.session_state.users_db[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "email": email
    }
    return True, "Registration successful"

def show_login():
    """Display login/register tabs and handle authentication"""
    st.title("🌶️ Chili Mate - Login")
    auth_result = None
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                auth_result = authenticate(username, password)
                if not auth_result["authenticated"]:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Username")
            new_email = st.text_input("Email (optional)")
            new_pass = st.text_input("Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Register"):
                if new_pass != confirm_pass:
                    st.error("Passwords don't match")
                else:
                    success, message = register_user(new_user, new_pass, new_email)
                    if success:
                        st.success(message)
                        # Auto-login after registration
                        auth_result = authenticate(new_user, new_pass)
                    else:
                        st.error(message)
    
    return auth_result

# SESSION STATE INITIALIZATION

def init_session_state():
    """Initialize all session state variables"""
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "authenticated": False,
            "username": None,
            "role": None,
            "email": None
        }
    
    # E-commerce states
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "wishlist" not in st.session_state:
        st.session_state.wishlist = []
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏡 Home"
    if "selected_product" not in st.session_state:
        st.session_state.selected_product = None
    
    # Inventory states
    if "inv_page" not in st.session_state:
        st.session_state.inv_page = "inventory"


# E-COMMERCE COMPONENTS

def get_product_filters(): 
    category_filter = st.sidebar.selectbox(
        "📂 Filter by Category",
        ["All"] + list(set(p["category"] for p in products))
    )
    sort_option = st.sidebar.selectbox(
        "🔽 Sort by",
        ["Price: Low to High", "Price: High to Low", "Rating", "Newest"]
    )
    return category_filter, sort_option

def sort_products(products, sort_option):
    if sort_option == "Price: Low to High":
        return sorted(products, key=lambda x: x["price"])
    elif sort_option == "Price: High to Low":
        return sorted(products, key=lambda x: x["price"], reverse=True)
    elif sort_option == "Rating":
        return sorted(products, key=lambda x: x.get("rating", 0), reverse=True)
    return products 

def display_products_card(product, col):
    with col:
        st.image(product.get("image", "https://via.placeholder.com/150"), width=150)
        st.subheader(product["name"])
        st.write(f"Price: Rp{product['price']:,.0f}".replace(",", "."))
        st.write(f"⭐ {product.get('rating', 'No rating')} / 5")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"📄 Details - {product['name']}", key=f"details_{product['name']}"):
                st.session_state.selected_product = product
                st.session_state.current_page = "🗂️ Products Details"
                st.rerun()
        with col2:
            if st.button(f"❤️ Add - {product['name']}", key=f"add_{product['name']}"):
                if product not in st.session_state.wishlist:
                    st.session_state.wishlist.append(product)
                    st.success(f"{product['name']} Added to Wishlist!")
                else:
                    st.warning(f"{product['name']} is already in your Wishlist!")

def get_filtered_products(products, category_filter, min_price, max_price):
    filtered = [p for p in products if
                (category_filter == "All" or p["category"] == category_filter)
                and min_price <= p["price"] <= max_price]
    return filtered
        
def show_products():
    st.header("🛍️ Products")
    category_filter, sort_option = get_product_filters()

    filtered_products = get_filtered_products(
        products, category_filter, 0, float("inf"))
    sorted_products = sort_products(filtered_products, sort_option)

    cols = st.columns(3)
    for idx, product in enumerate(sorted_products):
        display_products_card(product, cols[idx % 3])

def show_product_details():
    product = st.session_state.selected_product
    if not product:
        st.error("No product selected.")
        st.session_state.current_page = "🏡 Home"
        st.rerun()
        return
    
    st.image(product.get("image", "https://via.placeholder.com/300"), width=300)
    st.subheader(product["name"])
    st.write(f"Price: Rp{product['price']:,.0f}".replace(",", "."))
    st.write(f"📂 Category: {product['category']}")
    st.write(f"⭐ Rating {product.get('rating', 'No rating')} / 5")
    st.write(product.get("description", "No description available."))

    if "features" in product:
        st.subheader("🔹 Features:")
        for feature in product["features"]:
            st.write(f"- {feature}")
    
    if "specs" in product:
        st.subheader("🔧 Specifications")
        for key, value in product["specs"].items():
            st.write(f"**{key}:**{value}")

    if "reviews" in product:
        st.subheader("📄 Reviews")
        for review in product["reviews"]:
            st.write(f"**{review['user']}** ({review['rating']}/5): {review['comment']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        qty = st.number_input("Quantity", min_value=1, value=1, key="detail_qty")
    with col2:
        if st.button("🛒 Add to Cart"):
            item_in_cart = next((item for item in st.session_state.cart if item["name"] == product["name"]), None)
            if item_in_cart:
                item_in_cart["qty"] += qty
                item_in_cart["total"] = item_in_cart["qty"] * item_in_cart["price"]
            else:
                new_item = product.copy()
                new_item['qty'] = qty
                new_item['total'] = qty * product['price']
                st.session_state.cart.append(new_item)
            st.success(f"{product['name']} (x{qty}) added to cart!")
    with col3:
        if st.button("❤️ Add to Wishlist"):
            if product not in st.session_state.wishlist:
                st.session_state.wishlist.append(product)
                st.success(f"{product['name']} added to wishlist!")
            else:
                st.warning(f"{product['name']} is already in your wishlist!")

    if st.button("← Back to Products"):
        st.session_state.current_page = "🏡 Home"
        st.rerun()

def show_wishlist():
    st.header("❤️ Wishlist")

    if not st.session_state.wishlist:
        st.write("Your wishlist is empty.")
        return

    for idx, item in enumerate(st.session_state.wishlist[:]):  # Create a copy for iteration
        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader(f"{item['name']}")
            st.write(f"Unit Price: Rp{item['price']:,.0f}".replace(",", "."))

            qty_key = f"wishlist_qty_{idx}"
            if qty_key not in st.session_state:
                st.session_state[qty_key] = 1

            col_qty1, col_qty2, col_qty3 = st.columns([1, 2, 1])
            with col_qty1:
                if st.button("-", key=f"wishlist_minus_{idx}"):
                    if st.session_state[qty_key] > 1:
                        st.session_state[qty_key] -= 1
                        st.rerun()
            with col_qty2:
                st.session_state[qty_key] = st.number_input(
                    "Quantity", min_value=1, value=st.session_state[qty_key], 
                    key=f"wishlist_input_{idx}", label_visibility="collapsed"
                )
            with col_qty3:
                if st.button("+", key=f"wishlist_plus_{idx}"):
                    st.session_state[qty_key] += 1
                    st.rerun()

            total = st.session_state[qty_key] * item['price']
            st.write(f"**Total: Rp{total:,.0f}**".replace(",", "."))

        with col2:
            if st.button(f"🛒 Move to Cart", key=f"move_{idx}"):
                new_item = item.copy()
                new_item['qty'] = st.session_state[qty_key]
                new_item['total'] = total
                st.session_state.cart.append(new_item)
                st.session_state.wishlist.remove(item)
                st.success(f"{new_item['name']} (x{new_item['qty']}) moved to Cart.")
                st.rerun()
                
            if st.button(f"❌ Remove", key=f"remove_wish_{idx}"):
                st.session_state.wishlist.remove(item)
                st.success(f"{item['name']} removed from wishlist.")
                st.rerun()

def show_cart():
    st.header("🛒 Cart")

    if not st.session_state.cart:
        st.write("Your cart is empty.")
        return

    total_price = 0
    for idx, item in enumerate(st.session_state.cart[:]):  # Create a copy for iteration
        col1, col2 = st.columns([1, 4])

        with col1:
            st.image(item.get("image", "https://via.placeholder.com/100"), width=80)

        with col2:
            qty = item.get("qty", 1)
            price = item.get("price", 0)
            subtotal = qty * price
            total_price += subtotal

            st.markdown(f"**{item['name']}**")
            st.write(f"Unit Price: Rp{price:,.0f}".replace(",", "."))
            st.write(f"Quantity: {qty}")
            st.write(f"Subtotal: Rp{subtotal:,.0f}".replace(",", "."))

            if st.button(f"❌ Remove", key=f"remove_{idx}"):
                st.session_state.cart.remove(item)
                st.rerun()

    st.markdown("---")
    st.markdown(f"### 💰 Total Amount: Rp{total_price:,.2f}")

    if st.button("📂 Proceed to Checkout"):
        st.session_state.current_page = "🛍️ Checkout"
        st.rerun()

    if st.button("← Back to Products"):
        st.session_state.current_page = "🏡 Home"
        st.rerun()

def show_checkout():
    st.header("📂 Checkout")
    if not st.session_state.cart:
        st.write("Your cart is empty. Add products before checking out!")
        st.session_state.current_page = "🏡 Home"
        st.rerun()
        return
    
    show_checkout_form()
    
    if st.button("← Back to Cart"):
        st.session_state.current_page = "🛒 Cart"
        st.rerun()


# INVENTORY (ADMIN)
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE NOT NULL,
                 stock INTEGER NOT NULL,
                 price REAL NOT NULL)''')
    conn.commit()
    conn.close()

# Product constants
CHILI_PRODUCTS = [
    "Cabe Rawit Hijau", "Cabe Rawit Putih", "Cabe Hijau Keriting",
    "Cabe Rawit Merah", "Cabe Merah Ori", "Cabe Merah Keriting"
]

def format_currency(value):
    """Format numbers as Rp. with thousand separators"""
    return f"Rp. {int(value):,}".replace(",", ".")

def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL,
                  stock INTEGER NOT NULL,
                  price REAL NOT NULL)''')
    conn.commit()
    conn.close()

def get_inventory():
    """Get inventory with formatted currency values"""
    conn = sqlite3.connect('inventory.db')
    df = pd.read_sql("SELECT id, name AS 'Nama Barang', stock AS 'Stok', price AS 'Harga' FROM inventory", conn)
    conn.close()
    

    df["Harga Formatted"] = df["Harga"].apply(format_currency)
    df["Total"] = df["Stok"] * df["Harga"]
    df["Total Formatted"] = df["Total"].apply(format_currency)
    return df

def update_stock(product_name, quantity_change):
    conn = None
    try:
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
     
        c.execute("SELECT id, stock FROM inventory WHERE name=?", (product_name,))
        row = c.fetchone()
        if not row:
            return False, "Produk tidak ditemukan"
        
        product_id, current_stock = row
        new_stock = current_stock + quantity_change
        
        if new_stock < 0:
            return False, "Stok tidak boleh negatif"
        
        c.execute("UPDATE inventory SET stock=? WHERE id=?", (new_stock, product_id))
        conn.commit()
        return True, "Stok berhasil diperbarui"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error: {str(e)}"
    finally:
        if conn:
            conn.close()

#Buat Tambah produk baru
def add_product(name, stock, price):
    conn = None
    try:
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("INSERT INTO inventory (name, stock, price) VALUES (?, ?, ?)", (name, stock, price))
        conn.commit()
        return True, "Produk berhasil ditambahkan"
    except sqlite3.IntegrityError:
        return False, "Produk sudah ada"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error: {str(e)}"
    finally:
        if conn:
            conn.close()

def export_inventory():
    df = get_inventory()
    csv = df.to_csv(index=False)
    st.download_button("📥 Export to CSV", data=csv, file_name="inventory_export.csv", mime="text/csv")

# Tampilan halaman inventory
def show_inventory_page():
    st.header("📦 Manajemen Inventaris")
    df = get_inventory()
    
    st.dataframe(
        df[["Nama Barang", "Stok", "Harga Formatted", "Total Formatted"]]
        .rename(columns={
            "Harga Formatted": "Harga",
            "Total Formatted": "Total"
        }),
        hide_index=True,
        use_container_width=True
    )
    
    export_inventory()

    st.subheader("🔽 Kurangi Stok")
    inventory_df = get_inventory()
    product_names = CHILI_PRODUCTS

    selected_product = st.selectbox("Pilih Barang", product_names)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        qty = st.number_input("Jumlah Pengurangan", min_value=1, step=1)
    with col2:
        if st.button("Kurangi"):
            success, msg = update_stock(selected_product, -qty)
            if success:
                st.success(msg)
            else:
                st.error(msg)

def get_all_journal_entries():
    """Get all journal entries"""
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT id, date, debit_account, credit_account, amount, description FROM journal ORDER BY date")
    entries = c.fetchall()
    conn.close()
    return entries

def add_journal_entry(date, debit_account, credit_account, amount, description=""):
    """Add new journal entry"""
    try:
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('''INSERT INTO journal 
                    (date, debit_account, credit_account, amount, description)
                    VALUES (?, ?, ?, ?, ?)''',
                 (date, debit_account, credit_account, amount, description))
        conn.commit()
        return True, "Journal entry added successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def load_inventory_data():
    """Load inventory data"""
    init_user_database()
    rows = get_all_items()
    if rows:
        return pd.DataFrame(rows, columns=["ID", "Nama Barang", "Stok", "Harga"])
    return pd.DataFrame(columns=["ID", "Nama Barang", "Stok", "Harga"])

def load_journal_data():
    """Load journal data"""
    init_user_database()
    rows = get_all_journal_entries()
    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Tanggal", "Akun Debit", "Akun Kredit", "Jumlah", "Keterangan"])

        df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.strftime('%d/%m/%Y')
        return df
    return pd.DataFrame(columns=["ID", "Tanggal", "Akun Debit", "Akun Kredit", "Jumlah", "Keterangan"])

def format_currency(value):
    """Format numbers as Rp. with thousand separators"""
    return f"Rp. {int(value):,}".replace(",", ".")

def get_inventory():
    """Get inventory with formatted currency columns"""
    conn = sqlite3.connect('inventory.db')
    df = pd.read_sql("SELECT id, name AS 'Nama Barang', stock AS 'Stok', price AS 'Harga' FROM inventory", conn)
    conn.close()
    
    df['Total'] = df['Stok'] * df['Harga']
    df['Harga Formatted'] = df['Harga'].apply(format_currency)
    df['Total Formatted'] = df['Total'].apply(format_currency)
    
    return df

def show_inventory_page():
    st.header("📦 Manajemen Inventaris")
    df = get_inventory()
    
    st.subheader("📋 Inventaris Saat Ini")
    st.dataframe(
        df[['Nama Barang', 'Stok', 'Harga Formatted', 'Total Formatted']]
        .rename(columns={
            'Harga Formatted': 'Harga', 
            'Total Formatted': 'Total'
        }),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Harga": st.column_config.TextColumn("Harga (Rp)"),
            "Total": st.column_config.TextColumn("Total (Rp)")
        }
    )

    export_inventory()

    # ➕ Add Product Form 
    st.subheader("➕ Tambah Produk Baru")
    with st.form("add_product_form"):
        name = st.selectbox("Nama Produk", CHILI_PRODUCTS)
        stock = st.number_input("Stok Awal", min_value=0, step=1)
        price = st.number_input("Harga Satuan", min_value=0, step=1000)
        
        if st.form_submit_button("Tambah Produk"):
            success, msg = add_product(name, stock, price)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # 🔽 Reduce Stock Form 
    st.subheader("🔽 Kurangi Stok")
    if not df.empty:
        selected_product = st.selectbox(
            "Pilih Barang", 
            df['Nama Barang'].unique(),
            key="reduce_select"
        )
        product_info = df[df['Nama Barang'] == selected_product].iloc[0]
        st.write(f"Stok tersedia: {product_info['Stok']}")
        reduce_qty = st.number_input(
            "Jumlah Pengurangan",
            min_value=1,
            max_value=product_info['Stok'],
            value=1,
            key="reduce_qty"
        )        
        if st.button("Kurangi Stok", key="reduce_button"):
            success, msg = update_stock(selected_product, -reduce_qty)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    else:
        st.warning("Tidak ada produk untuk dikurangi")

# Jurnal Umum
def jurnal_umum_page():
    """General journal page"""
    st.header("📝 Jurnal Umum")
    
    st.subheader("➕ Input Entri Jurnal")
    with st.form("journal_form"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal")
            akun_debit = st.text_input("Akun Debit")
        with col2:
            akun_kredit = st.text_input("Akun Kredit")
            jumlah = st.number_input("Jumlah (Rp)", min_value=0.0)
        keterangan = st.text_area("Keterangan")
        
        if st.form_submit_button("Simpan Entri"):
            if not all([tanggal, akun_debit, akun_kredit, jumlah > 0]):
                st.error("❌ Harap isi semua field dengan benar!")
            else:
                tgl_str = tanggal.strftime("%Y-%m-%d")
                success, msg = add_journal_entry(tgl_str, akun_debit, akun_kredit, jumlah, keterangan)
                if success:
                    st.success("✅ Entri jurnal berhasil disimpan!")
                    st.rerun()
                else:
                    st.error(f"❌ Gagal menyimpan: {msg}")

    st.subheader("📋 Daftar Entri Jurnal")
    df_jurnal = load_journal_data()
    
    if df_jurnal.empty:
        st.info("Belum ada entri jurnal.")
    else:
        display_df = df_jurnal.copy()
        display_df["Jumlah"] = display_df["Jumlah"].apply(format_currency)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "Jumlah": st.column_config.NumberColumn(
                    "Jumlah",
                    format="Rp. %d"  
                )
            }
        )
# Buku Besar       
def buku_besar_page():
    """General ledger page with formatted currency"""
    st.header("📚 Buku Besar")
    
    df_jurnal = load_journal_data()
    
    if df_jurnal.empty:
        st.info("Belum ada data untuk ditampilkan.")
        return
    
    akun_options = sorted(set(df_jurnal["Akun Debit"].tolist() + df_jurnal["Akun Kredit"].tolist()))
    selected_account = st.selectbox("Pilih Akun", akun_options)
    
    debit_trans = df_jurnal[df_jurnal["Akun Debit"] == selected_account]
    credit_trans = df_jurnal[df_jurnal["Akun Kredit"] == selected_account]
    
    ledger_data = []
    
    # Add debit entries
    for _, row in debit_trans.iterrows():
        ledger_data.append({
            "Tanggal": row["Tanggal"],
            "Keterangan": row["Keterangan"],
            "Referensi": f"J-{row['ID']}",
            "Debit": row["Jumlah"], 
            "Kredit": 0,
            "Debit Formatted": format_currency(row["Jumlah"]),  
            "Kredit Formatted": "0"
        })
    
    # Add credit entries
    for _, row in credit_trans.iterrows():
        ledger_data.append({
            "Tanggal": row["Tanggal"],
            "Keterangan": row["Keterangan"],
            "Referensi": f"J-{row['ID']}",
            "Debit": 0,
            "Kredit": row["Jumlah"],  
            "Debit Formatted": "0",
            "Kredit Formatted": format_currency(row["Jumlah"])
        })
    
    if not ledger_data:
        st.info(f"Tidak ada transaksi untuk akun {selected_account}")
        return
    
    df_ledger = pd.DataFrame(ledger_data)
    df_ledger["Saldo"] = (df_ledger["Debit"] - df_ledger["Kredit"]).cumsum()
    df_ledger["Saldo Formatted"] = df_ledger["Saldo"].apply(format_currency)
    
    st.dataframe(
        df_ledger[[
            "Tanggal", 
            "Keterangan", 
            "Referensi", 
            "Debit Formatted", 
            "Kredit Formatted", 
            "Saldo Formatted"
        ]].rename(columns={
            "Debit Formatted": "Debit",
            "Kredit Formatted": "Kredit",
            "Saldo Formatted": "Saldo"
        }),
        use_container_width=True,
        column_config={
            "Debit": st.column_config.TextColumn("Debit (Rp)"),
            "Kredit": st.column_config.TextColumn("Kredit (Rp)"),
            "Saldo": st.column_config.TextColumn("Saldo (Rp)")
        }
    )

# Neraca Saldo
def neraca_saldo_page():
    """Trial balance page with formatted currency"""
    st.header("📑 Neraca Saldo")
    
    df_jurnal = load_journal_data()
    
    if df_jurnal.empty:
        st.info("Belum ada data untuk ditampilkan.")
        return
    
    neraca = pd.concat([
        df_jurnal.groupby("Akun Debit")["Jumlah"].sum().rename("Debit"),
        df_jurnal.groupby("Akun Kredit")["Jumlah"].sum().rename("Kredit")
    ], axis=1).fillna(0)
    
    neraca = neraca.reset_index().rename(columns={"index": "Akun"})
    
    display_neraca = neraca.copy()
    display_neraca["Debit"] = display_neraca["Debit"].apply(format_currency)
    display_neraca["Kredit"] = display_neraca["Kredit"].apply(format_currency)
    
    st.dataframe(
        display_neraca,
        use_container_width=True,
        column_config={
            "Akun": "Akun",
            "Debit": st.column_config.TextColumn("Debit (Rp)"),
            "Kredit": st.column_config.TextColumn("Kredit (Rp)")
        }
    )
    
    total_debit = neraca["Debit"].sum()
    total_kredit = neraca["Kredit"].sum()
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Debit", format_currency(total_debit))
    with col2:
        st.metric("Total Kredit", format_currency(total_kredit))
    
    if abs(total_debit - total_kredit) > 0.01:
        st.error("⚠️ Neraca tidak seimbang!")
    else:
        st.success("✓ Neraca seimbang")


# APPLICATION ROUTERS
def ecommerce_router():
    logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.jpg")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=200)
    else:
        st.sidebar.error("❌ Logo file not found!")
    st.sidebar.title(f"🛒 Ecommerce (Welcome {st.session_state.auth['username']})")

    st.sidebar.header("Menu")
    pages = ["🏡 Home", "🗂️ Products Details", "❤️ Wishlist", "🛒 Cart", "🛍️ Checkout"]
    st.session_state.current_page = st.sidebar.radio("Go to", pages, key="ecom_radio")
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = {"authenticated": False}
        st.session_state.current_page = "🏡 Home"
        st.session_state.cart = []
        st.session_state.wishlist = []
        st.rerun()

def inventory_router():
    logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.jpg")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=200)
    else:
        st.sidebar.error("❌ Logo file not found!")
    st.sidebar.title(f"📦 Inventory (Welcome {st.session_state.auth['username']})")
    page = st.sidebar.radio("Menu", ["Inventory", "Jurnal Umum", "Buku Besar", "Neraca Saldo"], key="inv_radio")
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = {"authenticated": False}
        st.rerun()
    
    if page == "Inventory":
        show_inventory_page()
    elif page == "Jurnal Umum":
        jurnal_umum_page()
    elif page == "Buku Besar":
        buku_besar_page()
    else:
        neraca_saldo_page()


# MAIN APPLICATION
def main():
    st.set_page_config(
        page_title="Chili Mate",
        page_icon="🌶️",
        layout="wide"
    )
    
    init_user_database()
    create_table()
    init_session_state()
    
    if not st.session_state.auth["authenticated"]:
        auth_result = show_login()
        if auth_result and auth_result["authenticated"]:
            st.session_state.auth = auth_result
            st.rerun()
        return 

    if st.session_state.auth["role"] in ["admin", "staff"]:
        inventory_router()
    else:
        ecommerce_router()
        
   
        page_handlers = {
            "🏡 Home": show_products,
            "🗂️ Products Details": show_product_details,
            "❤️ Wishlist": show_wishlist,
            "🛒 Cart": show_cart,
            "🛍️ Checkout": show_checkout
        }
        
        if st.session_state.current_page in page_handlers:
            page_handlers[st.session_state.current_page]()

if __name__ == "__main__":
    main()