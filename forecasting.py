import pandas as pd
import numpy as np

def predict_and_recommend(df_product, forecast_days=14, lead_time=3, current_stock=0, service_level_z=1.65):
    """
    Memprediksi penjualan dengan Weighted Moving Average + Efek Akhir Pekan,
    serta menghitung Safety Stock, Reorder Point, dan Saran Kulakan.
    """
    df = df_product.copy().sort_values("tanggal_transaksi")
    
    # Hitung rata-rata dan standar deviasi harian (30 hari terakhir)
    recent_df = df.tail(30)
    avg_daily_demand = recent_df["jumlah_terjual"].mean()
    std_daily_demand = recent_df["jumlah_terjual"].std()
    if np.isnan(std_daily_demand):
        std_daily_demand = 0.0

    # Hitung rasio penjualan akhir pekan (Jumat-Minggu) vs hari kerja
    df["is_weekend"] = df["tanggal_transaksi"].dt.dayofweek.isin([4, 5, 6])
    weekday_avg = df[~df["is_weekend"]]["jumlah_terjual"].mean()
    weekend_avg = df[df["is_weekend"]]["jumlah_terjual"].mean()
    weekend_ratio = (weekend_avg / weekday_avg) if weekday_avg > 0 else 1.0

    # Buat tanggal prediksi ke depan
    last_date = df["tanggal_transaksi"].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)
    
    predictions = []
    for d in future_dates:
        multiplier = weekend_ratio if d.dayofweek in [4, 5, 6] else 1.0
        # Sesuaikan baseline agar tetap proporsional
        base = avg_daily_demand / (0.7 + 0.3 * weekend_ratio)
        pred_qty = max(1, round(base * multiplier))
        predictions.append({
            "tanggal_transaksi": d,
            "prediksi_terjual": pred_qty
        })
        
    df_forecast = pd.DataFrame(predictions)
    total_predicted_demand = df_forecast["prediksi_terjual"].sum()

    # Rumus Manajemen Inventaris
    # 1. Safety Stock = Z * std_dev * sqrt(lead_time)
    safety_stock = int(np.ceil(service_level_z * std_daily_demand * np.sqrt(lead_time)))
    
    # 2. Reorder Point (ROP) = (Permintaan Harian * Lead Time) + Safety Stock
    reorder_point = int(np.ceil((avg_daily_demand * lead_time) + safety_stock))
    
    # 3. Saran Kulakan = (Prediksi selama periode + Safety Stock) - Stok Saat Ini
    recommended_order = max(0, int(np.ceil((total_predicted_demand + safety_stock) - current_stock)))

    metrics = {
        "avg_daily": round(avg_daily_demand, 1),
        "total_forecast": int(total_predicted_demand),
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "recommended_order": recommended_order
    }
    
    return df_forecast, metrics