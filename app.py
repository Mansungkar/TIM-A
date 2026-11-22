import streamlit as st
import pandas as pd
import urllib.parse
from data_processor import load_and_clean_data
from forecasting import predict_and_recommend
from visualizer import plot_sales_forecast

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Asisten Restock & Ramalan UMKM",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS UNTUK TAMPILAN MODERN ---
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

# --- 4. HEADER UTAMA SETELAH LOGIN ---
st.markdown(f"""
    <div class="hero-banner">
        <h1>📦 {st.session_state.get('store_name', 'Toko Mitra UMKM')} — Asisten Restock AI</h1>
        <p>Pemantauan kesehatan stok otomatis, prediksi penjualan harian, dan order cepat ke supplier.</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR: PROFIL, INPUT & PARAMETER ---
with st.sidebar:
    st.markdown(f"👤 **{st.session_state['user_name']}**")
    st.caption(f"Peran: {st.session_state['user_role']}")
    st.divider()

    st.header("1. Sumber Data Transaksi")
    uploaded_file = st.file_uploader("Unggah file CSV atau Excel (.xlsx)", type=["csv", "xlsx"])

    try:
        df = load_and_clean_data(uploaded_file)
    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
        st.stop()

    sample_csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Unduh Contoh Format CSV",
        data=sample_csv,
        file_name="template_transaksi.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()
    st.header("2. Parameter Prediksi & Stok")
    product_list = df["nama_produk"].unique().tolist()
    selected_product = st.selectbox("Pilih Produk (Analisis Detail)", product_list)

    current_stock = st.number_input("Sisa Stok di Gudang Saat Ini", min_value=0, value=50, step=5)
    forecast_days = st.slider("Periode Prediksi (Hari ke depan)", min_value=7, max_value=30, value=14)
    lead_time = st.number_input("Waktu Tunggu Supplier / Lead Time (Hari)", min_value=1, max_value=14, value=3)

    st.divider()
    if st.button("🚪 Keluar (Logout)", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

if uploaded_file is None:
    st.info("ℹ️ Saat ini menampilkan **data simulasi bawaan**. Unggah file CSV/Excel di sidebar kiri untuk memakai data tokomu sendiri.")

# --- 6. PERHITUNGAN PRODUK TERPILIH ---
df_product = df[df["nama_produk"] == selected_product]
df_forecast, metrics = predict_and_recommend(
    df_product=df_product,
    forecast_days=forecast_days,
    lead_time=lead_time,
    current_stock=current_stock
)

# --- 7. KARTU METRIK PRODUK TERPILIH ---
st.subheader(f"📊 Ringkasan Analisis: {selected_product}")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Rata-rata Terjual / Hari", f"{metrics['avg_daily']} unit")
col2.metric(f"Prediksi {forecast_days} Hari", f"{metrics['total_forecast']} unit")
col3.metric("Batas Pesan Ulang (ROP)", f"{metrics['reorder_point']} unit", help=f"Termasuk Safety Stock: {metrics['safety_stock']} unit")
col4.metric("Rekomendasi Kulakan", f"{metrics['recommended_order']} unit")

if current_stock <= metrics["reorder_point"]:
    st.warning(f"⚠️ **Stok Menipis!** Sisa stok ({current_stock} unit) berada di bawah batas aman ({metrics['reorder_point']} unit). Segera pesan **{metrics['recommended_order']} unit**.")
else:
    st.success(f"✅ **Stok Aman.** Sisa stok ({current_stock} unit) masih mencukupi hingga titik pemesanan ulang berikutnya.")

st.divider()

# --- 8. NAVIGASI TAB UTAMA ---
tab_batch, tab_grafik, tab_data, tab_ekspor = st.tabs([
    "🚨 Cek Semua Produk & Order WA",
    "📈 Grafik Prediksi Produk",
    "📋 Detail Angka Harian",
    "⬇️ Ekspor Laporan"
])

# TAB 1: PEMINDAIAN SEMUA PRODUK & WHATSAPP GENERATOR
with tab_batch:
    st.subheader("Pemindaian Otomatis Seluruh Produk (Batch Alert)")
    st.caption(f"Simulasi kondisi seluruh SKU dengan asumsi sisa stok masing-masing produk saat ini = {current_stock} unit.")

    semua_hasil = []
    for prod in product_list:
        df_p = df[df["nama_produk"] == prod]
        _, m_p = predict_and_recommend(
            df_product=df_p,
            forecast_days=forecast_days,
            lead_time=lead_time,
            current_stock=current_stock
        )
        status_label = "🔴 Perlu Restock" if current_stock <= m_p["reorder_point"] else "🟢 Aman"
        semua_hasil.append({
            "Nama Produk": prod,
            "Rata2 Harian": f"{m_p['avg_daily']} unit",
            "Batas Aman (ROP)": f"{m_p['reorder_point']} unit",
            "Saran Kulakan": m_p["recommended_order"],
            "Status": status_label
        })

    df_semua = pd.DataFrame(semua_hasil)
    perlu_order = df_semua[df_semua["Status"] == "🔴 Perlu Restock"]

    kol_tabel, kol_wa = st.columns([1.4, 1])
    with kol_tabel:
        st.dataframe(df_semua, use_container_width=True, hide_index=True)

    with kol_wa:
        st.markdown("#### 📲 Generator Pesan Order WhatsApp")
        if len(perlu_order) == 0:
            st.success("Semua produk dalam status Aman. Tidak ada daftar belanja yang perlu dikirim.")
        else:
            no_wa = st.text_input("Nomor WA Supplier (awali 62)", value="6281234567890")
            daftar_item = "\n".join([
                f"- {r['Nama Produk']}: {r['Saran Kulakan']} unit"
                for _, r in perlu_order.iterrows()
            ])
            teks_wa = (
                f"Halo Supplier, kami dari *{st.session_state.get('store_name', 'Toko Mitra UMKM')}* "
                f"ingin memesan restock barang berikut:\n\n"
                f"{daftar_item}\n\n"
                f"Mohon konfirmasi ketersediaan dan total tagihannya. Terima kasih."
            )
            pesan_edit = st.text_area("Edit Pesan Sebelum Kirim:", value=teks_wa, height=175)
            link_wa = f"https://wa.me/{no_wa}?text={urllib.parse.quote(pesan_edit)}"
            st.link_button("🚀 Kirim Order ke WhatsApp", link_wa, type="primary", use_container_width=True)

# TAB 2: GRAFIK PREDIKSI
with tab_grafik:
    fig = plot_sales_forecast(df_product, df_forecast, selected_product)
    st.plotly_chart(fig, use_container_width=True)

# TAB 3: DETAIL ANGKA HARIAN
with tab_data:
    st.dataframe(df_forecast, use_container_width=True)

# TAB 4: EKSPOR LAPORAN
with tab_ekspor:
    st.subheader("Unduh Hasil Rekomendasi Restock")
    export_df = df_forecast.copy()
    export_df["nama_produk"] = selected_product
    export_df["saran_kulakan_total"] = metrics["recommended_order"]
    export_df["batas_pesan_ulang_rop"] = metrics["reorder_point"]

    csv_result = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"⬇️ Unduh Laporan Prediksi ({selected_product}) - CSV",
        data=csv_result,
        file_name=f"rekomendasi_restock_{selected_product.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        type="primary"
    )