import pandas as pd
import numpy as np

def generate_dummy_data():
    """Membuat data simulasi transaksi harian selama 180 hari (6 bulan)."""
    np.random.seed(42)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=180)
    data = []
    products = {
        "Kopi Susu Gula Aren": (45, 12),
        "Roti Bakar Cokelat": (30, 8),
        "Es Teh Manis Jumbo": (60, 15)
    }
    for sku, (base_demand, std_dev) in products.items():
        for d in dates:
            weekend_boost = 1.3 if d.dayofweek in [4, 5, 6] else 1.0
            trend = (d - dates[0]).days * 0.03
            qty = max(1, int(np.random.normal(base_demand * weekend_boost + trend, std_dev)))
            data.append({
                "tanggal_transaksi": d,
                "nama_produk": sku,
                "jumlah_terjual": qty
            })
    return pd.DataFrame(data)

def load_and_clean_data(uploaded_file):
    """Membaca file CSV/Excel yang diunggah dan membersihkan format datanya."""
    if uploaded_file is None:
        return generate_dummy_data()
    
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    # Validasi kolom wajib
    required_cols = {"tanggal_transaksi", "nama_produk", "jumlah_terjual"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"File harus memiliki kolom: {', '.join(required_cols)}")
        
    # Konversi tipe data & agregasi harian per produk
    df["tanggal_transaksi"] = pd.to_datetime(df["tanggal_transaksi"])
    df["jumlah_terjual"] = pd.to_numeric(df["jumlah_terjual"], errors="coerce").fillna(0)
    
    df_clean = (
        df.groupby(["tanggal_transaksi", "nama_produk"], as_index=False)["jumlah_terjual"]
        .sum()
        .sort_values("tanggal_transaksi")
    )
    return df_clean