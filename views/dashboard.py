import streamlit as st
import pandas as pd
import urllib.parse
from forecasting import predict_and_recommend


def show_dashboard():
    st.markdown("""
        <div class="hero-banner">
            <h1>🚨 Ringkasan Kondisi Toko & Peringatan Restock</h1>
            <p>Pemindaian otomatis seluruh produk untuk mendeteksi barang kritis dan menyiapkan order ke supplier.</p>
        </div>
    """, unsafe_allow_html=True)

    df = st.session_state["df_clean"]
    current_stock = st.session_state.get("current_stock", 50)
    forecast_days = st.session_state.get("forecast_days", 14)
    lead_time = st.session_state.get("lead_time", 3)

    if st.session_state.get("is_sample", True):
        st.info("ℹ️ Menampilkan **data simulasi bawaan**. Unggah file CSV/Excel di sidebar kiri untuk memakai data tokomu sendiri.")

    product_list = df["nama_produk"].unique().tolist()

    # --- PEMINDAIAN BATCH ALERT SEMUA PRODUK ---
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
            "Rata-rata / Hari": f"{m_p['avg_daily']} unit",
            "Batas Aman (ROP)": f"{m_p['reorder_point']} unit",
            "Saran Kulakan": m_p["recommended_order"],
            "Status": status_label
        })

    df_semua = pd.DataFrame(semua_hasil)
    perlu_order = df_semua[df_semua["Status"] == "🔴 Perlu Restock"]

    # --- KARTU KPI RINGKASAN TOKO ---
    k1, k2, k3 = st.columns(3)
    k1.metric("Total SKU Terpantau", f"{len(df_semua)} Produk")
    k2.metric(
        "Perlu Segera Restock",
        f"{len(perlu_order)} Produk",
        delta=f"{len(perlu_order)} item kritis" if len(perlu_order) > 0 else "Semua aman",
        delta_color="inverse"
    )
    k3.metric("Total Saran Kulakan", f"{int(perlu_order['Saran Kulakan'].sum())} Unit")

    st.divider()

    # --- TABEL STATUS & GENERATOR ORDER WHATSAPP ---
    kol_tabel, kol_wa = st.columns([1.45, 1])

    with kol_tabel:
        st.subheader("📋 Status Kesehatan Stok Seluruh Produk")
        st.caption(f"Simulasi memakai sisa stok saat ini = {current_stock} unit dan lead time = {lead_time} hari.")
        st.dataframe(df_semua, use_container_width=True, hide_index=True)

    with kol_wa:
        st.subheader("📲 Order Cepat ke Supplier (WA)")
        if len(perlu_order) == 0:
            st.success("Semua stok produk dalam status Aman. Belum perlu memesan ke supplier.")
        else:
            no_wa = st.text_input("Nomor WhatsApp Supplier (awali 62)", value="6281234567890")
            daftar_item = "\n".join([
                f"- {r['Nama Produk']}: {r['Saran Kulakan']} unit"
                for _, r in perlu_order.iterrows()
            ])
            nama_toko = st.session_state.get("store_name", "Toko Mitra UMKM")
            teks_wa = (
                f"Halo Supplier, kami dari *{nama_toko}* ingin melakukan pemesanan restock barang berikut:\n\n"
                f"{daftar_item}\n\n"
                f"Mohon informasi ketersediaan dan total tagihannya. Terima kasih."
            )
            pesan_edit = st.text_area("Pratinjau Pesan (Bisa Diedit):", value=teks_wa, height=180)
            link_wa = f"https://wa.me/{no_wa}?text={urllib.parse.quote(pesan_edit)}"
            st.link_button("🚀 Kirim Pesan Order via WhatsApp", link_wa, type="primary", use_container_width=True)