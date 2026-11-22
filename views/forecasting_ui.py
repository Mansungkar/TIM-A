import streamlit as st
from data_processor import load_and_clean_data
from views.dashboard import show_dashboard
from views.forecasting_ui import show_forecasting

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Asisten Restock & Ramalan UMKM",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS GLOBAL ---
st.markdown("""
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        padding: 1.6rem 2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
    }
    .hero-banner h1 { margin: 0; font-size: 1.8rem; font-weight: 700; color: #FFFFFF; }
    .hero-banner p { margin: 0.4rem 0 0 0; font-size: 0.95rem; color: #DBEAFE; }
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2563EB;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SISTEM LOGIN SEDERHANA ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

AKUN_DEMO = {
    "owner@toko.id": {"password": "123", "role": "Owner / Admin", "nama": "Pemilik Toko"},
    "kasir@toko.id": {"password": "123", "role": "Kasir / Gudang", "nama": "Staf Kasir"}
}

if not st.session_state["logged_in"]:
    col_kiri, col_tengah, col_kanan = st.columns([1, 1.3, 1])
    with col_tengah:
        st.markdown("""
            <div class="hero-banner" style="text-align:center;">
                <h1>📦 Asisten Restock & Ramalan UMKM</h1>
                <p>Masuk ke dashboard toko untuk memantau stok dan prediksi penjualan.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            email = st.text_input("Email Pengguna", placeholder="Contoh: owner@toko.id")
            password = st.text_input("Kata Sandi", type="password", placeholder="Masukkan password")
            nama_toko = st.text_input("Nama Toko", value="Toko Mitra UMKM")
            masuk = st.form_submit_button("Masuk ke Dashboard", type="primary", use_container_width=True)

            if masuk:
                if email in AKUN_DEMO and AKUN_DEMO[email]["password"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = AKUN_DEMO[email]["role"]
                    st.session_state["user_name"] = AKUN_DEMO[email]["nama"]
                    st.session_state["store_name"] = nama_toko
                    st.rerun()
                else:
                    st.error("Email atau kata sandi salah.")

        with st.expander("🔑 Akun Demo untuk Uji Coba"):
            st.write("- **Owner:** `owner@toko.id` | Password: `123`")
            st.write("- **Kasir:** `kasir@toko.id` | Password: `123`")
    st.stop()

# --- 4. SIDEBAR: PROFIL, DATA & PARAMETER GLOBAL ---
with st.sidebar:
    st.markdown(f"### 🏪 {st.session_state.get('store_name', 'Toko Mitra UMKM')}")
    st.caption(f"👤 **{st.session_state['user_name']}** ({st.session_state['user_role']})")
    st.divider()

    st.header("1. Sumber Data Transaksi")
    uploaded_file = st.file_uploader("Unggah file CSV atau Excel (.xlsx)", type=["csv", "xlsx"])

    try:
        st.session_state["df_clean"] = load_and_clean_data(uploaded_file)
        st.session_state["is_sample"] = uploaded_file is None
    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
        st.stop()

    sample_csv = st.session_state["df_clean"].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Unduh Contoh Format CSV",
        data=sample_csv,
        file_name="template_transaksi.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()
    st.header("2. Parameter Stok & Prediksi")
    st.session_state["current_stock"] = st.number_input("Sisa Stok di Gudang Saat Ini", min_value=0, value=50, step=5)
    st.session_state["forecast_days"] = st.slider("Periode Prediksi (Hari ke depan)", min_value=7, max_value=30, value=14)
    st.session_state["lead_time"] = st.number_input("Waktu Tunggu Supplier / Lead Time (Hari)", min_value=1, max_value=14, value=3)

    st.divider()
    if st.button("🚪 Keluar (Logout)", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

# --- 5. NAVIGASI HALAMAN (MULTIPAGE ROUTER) ---
pages = [
    st.Page(show_dashboard, title="Ringkasan & Order WA", icon="🚨", default=True),
    st.Page(show_forecasting, title="Grafik & Simulasi Produk", icon="📈")
]
pg = st.navigation(pages)
pg.run()