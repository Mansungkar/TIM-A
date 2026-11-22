import plotly.graph_objects as go

def plot_sales_forecast(df_history, df_forecast, product_name):
    """Membuat grafik garis perbandingan penjualan historis dan hasil prediksi."""
    fig = go.Figure()

    # Garis Data Historis (60 hari terakhir agar grafik mudah dibaca)
    hist_recent = df_history.tail(60)
    fig.add_trace(go.Scatter(
        x=hist_recent["tanggal_transaksi"],
        y=hist_recent["jumlah_terjual"],
        mode="lines+markers",
        name="Penjualan Historis",
        line=dict(color="#2563EB", width=2)
    ))

    # Garis Prediksi
    fig.add_trace(go.Scatter(
        x=df_forecast["tanggal_transaksi"],
        y=df_forecast["prediksi_terjual"],
        mode="lines+markers",
        name="Prediksi Permintaan",
        line=dict(color="#F59E0B", width=2, dash="dash")
    ))

    fig.update_layout(
        title=f"Tren Penjualan & Prediksi: {product_name}",
        xaxis_title="Tanggal",
        yaxis_title="Jumlah Terjual (Unit)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig