import streamlit as st
from data_processor import load_and_clean_data
from forecasting import predict_and_recommend
from visualizer import plot_sales_forecast

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Asisten Restock & Ramalan UMKM", page_icon="📦", layout="wide")

st.title("📦 Peramal Penjualan & Rekomendasi Restock UMKM")

# --- SIDEBAR: INPUT & PARAMETER ---
st.sidebar.header("1. Sumber Data Transaksi")
uploaded_file = st.sidebar.file_uploader("Unggah file CSV atau Excel (.xlsx)", type=["csv", "xlsx"])

try:
    df = load_and_clean_data(uploaded_file)
    if uploaded_file is None:
except Exception as e:
    st.error(f"Gagal memproses file: {e}")
    st.stop()

# [BARU] Tombol Unduh Contoh Format CSV di Sidebar
sample_csv = df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="📥 Unduh Contoh Format CSV",
    data=sample_csv,
    file_name="template_transaksi.csv",
    mime="text/csv"
)

st.sidebar.header("2. Parameter Prediksi & Stok")
product_list = df["nama_produk"].unique().tolist()
selected_product = st.sidebar.selectbox("Pilih Produk (SKU)", product_list)

current_stock = st.sidebar.number_input("Sisa Stok di Gudang Saat Ini", min_value=0, value=50, step=5)
forecast_days = st.sidebar.slider("Periode Prediksi (Hari ke depan)", min_value=7, max_value=30, value=14)
lead_time = st.sidebar.number_input("Waktu Tunggu Supplier / Lead Time (Hari)", min_value=1, max_value=14, value=3)

# --- PROSES PERHITUNGAN ---
df_product = df[df["nama_produk"] == selected_product]
df_forecast, metrics = predict_and_recommend(
    df_product=df_product,
    forecast_days=forecast_days,
    lead_time=lead_time,
    current_stock=current_stock
)

# --- TAMPILAN METRIK UTAMA ---
st.subheader(f"Ringkasan Analisis: {selected_product}")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Rata-rata Terjual / Hari", f"{metrics['avg_daily']} unit")
col2.metric(f"Prediksi {forecast_days} Hari", f"{metrics['total_forecast']} unit")
col3.metric("Batas Pesan Ulang (ROP)", f"{metrics['reorder_point']} unit", help=f"Termasuk Safety Stock: {metrics['safety_stock']} unit")
col4.metric("Rekomendasi Kulakan", f"{metrics['recommended_order']} unit")

# Status Peringatan Stok
if current_stock <= metrics["reorder_point"]:
    st.warning(f"⚠️ **Stok Menipis!** Sisa stok ({current_stock} unit) sudah berada di bawah batas aman ({metrics['reorder_point']} unit). Segera lakukan pemesanan sebanyak **{metrics['recommended_order']} unit**.")
else:
    st.success(f"✅ **Stok Aman.** Sisa stok ({current_stock} unit) masih mencukupi hingga titik pemesanan ulang berikutnya.")

# --- GRAFIK & TABEL DETAIL ---
fig = plot_sales_forecast(df_product, df_forecast, selected_product)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Lihat Detail Angka Prediksi Harian"):
    st.dataframe(df_forecast, use_container_width=True)

# [BARU] Tombol Ekspor Laporan Hasil Rekomendasi di Bagian Paling Bawah
st.divider()
st.subheader("Ekspor Hasil Rekomendasi")

export_df = df_forecast.copy()
export_df["nama_produk"] = selected_product
export_df["saran_kulakan_total"] = metrics["recommended_order"]
export_df["batas_pesan_ulang_rop"] = metrics["reorder_point"]

csv_result = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label=f"⬇️ Unduh Laporan Prediksi ({selected_product}) - CSV",
    data=csv_result,
    file_name=f"rekomendasi_restock_{selected_product.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)
