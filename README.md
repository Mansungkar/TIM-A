# 📦 Peramal Penjualan & Rekomendasi Restock UMKM

Aplikasi berbasis web menggunakan Python dan Streamlit untuk memprediksi permintaan penjualan harian serta menghitung batas aman stok (*Safety Stock*), titik pemesanan ulang (*Reorder Point*), dan saran jumlah kulakan (*restock*).

## Struktur File Proyek
- `app.py` : Antarmuka utama aplikasi (Streamlit UI).
- `data_processor.py` : Pembersihan data, validasi kolom CSV/Excel, dan pembuatan data simulasi.
- `forecasting.py` : Algoritma peramalan permintaan (memperhitungkan tren dan lonjakan akhir pekan) serta kalkulasi inventaris.
- `visualizer.py` : Pembuatan grafik interaktif menggunakan Plotly.
- `requirements.txt` : Daftar library Python yang dibutuhkan.

## Cara Menjalankan Aplikasi di Laptop
1. Masuk ke folder proyek:
   ```bash
   cd proyek_produk_A