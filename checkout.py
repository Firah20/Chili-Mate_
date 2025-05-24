import streamlit as st
import time
from datetime import datetime
import random

# Konfigurasi halaman
st.set_page_config(page_title="Checkout Pembayaran", page_icon="💳", layout="wide")

def generate_order_id():
    """Generate random order ID"""
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

def show_checkout_form():
    st.title("🛒 Proses Checkout")
    
    cart_items = st.session_state.get("cart", [])
    
    # Hitung total
    subtotal = sum(item["price"] for item in cart_items)
    shipping_cost = 15000 if subtotal < 200000 else 0
    total = subtotal + shipping_cost
    
    # Layout dua kolom
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.header("Informasi Pengiriman")
        
        # Form informasi pengiriman
        with st.form("delivery_info"):
            full_name = st.text_input("Nama Lengkap*", placeholder="Nama penerima")
            phone = st.text_input("Nomor Telepon*", placeholder="08123456789")
            email = st.text_input("Email*", placeholder="email@contoh.com")
            
            st.markdown("---")
            
            address = st.text_area("Alamat Lengkap*", placeholder="Jl. Contoh No. 123, RT/RW, Kecamatan, Kota")
            postal_code = st.text_input("Kode Pos*", placeholder="12345")
            
            st.markdown("<p class='big-font'>Metode Pengiriman</p>", unsafe_allow_html=True)
            shipping_method = st.radio(
                "Pilihan:",
                ["Reguler (3-5 hari) - Rp 15.000", "Express (1-2 hari) - Rp 25.000", "Gratis Ongkir (min. belanja Rp 200.000)"],
                label_visibility="collapsed"
            )
            
            submitted = st.form_submit_button("Simpan Informasi Pengiriman")
            if submitted:
                st.success("Informasi pengiriman disimpan!")
    
    with col2:
        st.header("Ringkasan Pesanan")
        
        # Daftar produk
        st.markdown("<p class='big-font'>Produk Dipesan</p>", unsafe_allow_html=True)
        for item in cart_items:
            st.write(f"{item['name']}  - Rp {item['price'] }")
        
        st.markdown("---")
        
        # Ringkasan pembayaran
        st.markdown("<p class='big-font'>Ringkasan Pembayaran</p>", unsafe_allow_html=True)
        st.write(f"Subtotal: Rp {subtotal:,}")
        
        shipping_text = "Gratis" if shipping_cost == 0 else f"Rp {shipping_cost:,}"
        st.write(f"Biaya Pengiriman: {shipping_text}")
        
        st.markdown("---")
        st.markdown(f"**Total Pembayaran: Rp {total:,}**")
        
        # Pilihan metode pembayaran
        st.markdown("<p class='big-font'>Metode Pembayaran</p>", unsafe_allow_html=True)
        payment_method = st.radio(
            "Pilih metode pembayaran:",
            ["Virtual Account", "Kartu Kredit", "E-Wallet", "Retail Outlet"],
            label_visibility="collapsed"
        )
        
        # Detail berdasarkan metode pembayaran
        if payment_method == "Virtual Account":
            st.selectbox("Bank Tujuan", ["BCA", "Mandiri", "BNI", "BRI", "Bank Lainnya"])
            st.info("Virtual Account akan dibuat setelah Anda melanjutkan pembayaran")
        
        elif payment_method == "Kartu Kredit":
            cc_number = st.text_input("Nomor Kartu", placeholder="1234 5678 9012 3456")
            col1, col2 = st.columns(2)
            with col1:
                exp_date = st.text_input("Masa Berlaku (MM/YY)", placeholder="MM/YY")
            with col2:
                cvv = st.text_input("CVV", placeholder="123", type="password")
        
        elif payment_method == "E-Wallet":
            st.selectbox("Pilih E-Wallet", ["GoPay", "OVO", "Dana", "ShopeePay"])
            st.info("Anda akan diarahkan ke aplikasi e-wallet untuk menyelesaikan pembayaran")
        
        elif payment_method == "Retail Outlet":
            st.selectbox("Pilih Outlet", ["Alfamart", "Indomaret", "Lawson", "Pos Indonesia"])
            st.info("Simpan kode pembayaran dan bayar di outlet terdekat dalam 24 jam")
        
        # Tombol pembayaran
        if st.button("Lanjutkan Pembayaran", type="primary", use_container_width=True):
            process_payment(total, payment_method)

def process_payment(amount, method):
    """Simulasi proses pembayaran"""
    with st.spinner("Memproses pembayaran Anda..."):
        time.sleep(3)
        
        # Generate order ID
        order_id = generate_order_id()
        
        # Simpan data transaksi
        st.session_state.payment_data = {
            "order_id": order_id,
            "amount": amount,
            "method": method,
            "status": "success",
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        # Redirect ke halaman konfirmasi
        payment_confirmation()

def payment_confirmation():
    """Halaman konfirmasi pembayaran"""
    if not hasattr(st.session_state, "payment_data"):
        st.warning("Tidak ada data pembayaran. Silakan lakukan pembayaran terlebih dahulu.")
        time.sleep(2)
        st.experimental_rerun()
    
    payment_data = st.session_state.payment_data
    
    st.title("✅ Pembayaran Berhasil")
    st.markdown(f"<div class='success-box'>"
                f"<h3>Terima kasih telah berbelanja!</h3>"
                f"<p>ID Pesanan: <strong>{payment_data['order_id']}</strong></p>"
                f"<p>Total Pembayaran: <strong>Rp {payment_data['amount']:,}</strong></p>"
                f"<p>Metode Pembayaran: <strong>{payment_data['method']}</strong></p>"
                f"<p>Waktu Transaksi: <strong>{payment_data['timestamp']}</strong></p>"
                f"<p>Status: <strong style='color:green'>Berhasil</strong></p>"
                f"</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Invoice sederhana
    st.header("Invoice Pembayaran")
    
    invoice_content = f"""
    ==============================
    INVOICE PEMBAYARAN
    ==============================
    No. Invoice: {payment_data['order_id']}
    Tanggal: {payment_data['timestamp']}
    
    Detail Pembayaran:
    - Subtotal: Rp {payment_data['amount'] - 15000:,}
    - Biaya Pengiriman: Rp 15,000
    - Total: Rp {payment_data['amount']:,}
    
    Metode Pembayaran: {payment_data['method']}
    Status: Lunas
    
    Terima kasih telah berbelanja!
    ==============================
    """
    
    st.code(invoice_content)
    
    # Tombol download invoice
    st.download_button(
        label="📥 Download Invoice",
        data=invoice_content,
        file_name=f"invoice_{payment_data['order_id']}.txt",
        mime="text/plain"
    )
    
    # Tombol kembali ke beranda
    if st.button("Kembali ke Beranda", use_container_width=True):
        del st.session_state.payment_data
        st.experimental_rerun()

# Routing sederhana
if hasattr(st.session_state, "payment_data") and st.session_state.payment_data.get("status") == "success":
    payment_confirmation()
else:
    show_checkout_form()