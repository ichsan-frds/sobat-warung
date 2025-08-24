import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
try:
    from darts import TimeSeries
except ImportError:
    print("ERROR: Library Darts tidak terinstal. Jalankan: pip install darts")
    exit()

rules = pd.read_csv('./data/association_rules.csv')

rules['antecedents'] = rules['antecedents'].apply(lambda x: [i.strip() for i in str(x).split(",")])
rules['consequents'] = rules['consequents'].apply(lambda x: [i.strip() for i in str(x).split(",")])

def get_bundling(product: str, top_n: int = 1):
    recs = rules[rules['antecedents'].apply(lambda x: product in x)]
    recs = recs.sort_values(by="confidence", ascending=False)
    result = recs.head(top_n)[['antecedents', 'consequents', 'confidence', 'lift']]
    
    return result.to_dict(orient='records')

class DummyPipeline:
    def inverse_transform(self, data): return data
    def transform(self, data): return data

class DummyModel:
    def predict(self, n, series):
        predictions = []
        for ts in series:
            last_value = ts.last_value() * 0.98  # Prediksi besok = 98% dari hari ini
            start_date = ts.end_time() + ts.freq
            pred_dates = pd.date_range(start=start_date, periods=n, freq=ts.freq)
            # Kembalikan prediksi dengan static covariates (yaitu 'type') yang sama
            predictions.append(TimeSeries.from_times_and_values(pred_dates, [last_value] * n, static_covariates=ts.static_covariates))
        return predictions

pipelines_dict = {
    "BEVERAGES": DummyPipeline(),
    "GROCERY I": DummyPipeline(),
    "BREAD/BAKERY": DummyPipeline()
}
models_dict = {
    "BEVERAGES": [DummyModel()],
    "GROCERY I": [DummyModel()],
    "BREAD/BAKERY": [DummyModel()]
}
product_to_family_map = {
    "bengbeng": "GROCERY I", "chitato": "GROCERY I", "indomie goreng": "GROCERY I",
    "teh botol": "BEVERAGES", "aqua 600ml": "BEVERAGES", "kopi kapal api": "BEVERAGES",
    "roma kelapa": "BREAD/BAKERY", "sari roti": "BREAD/BAKERY"
}
print("✅ Artefak dummy (per tipe) berhasil dibuat.")

def map_and_agg_sales_by_type(daily_sales_df, product_map, warung_info):
    """Menerjemahkan nama produk dan mengagregasi penjualan per family DAN tipe toko."""
    print("\n  - Langkah 1: Memetakan & mengagregasi laporan harian per Tipe Toko...")
    df = daily_sales_df.copy()
    df['family'] = df['nama_produk'].str.lower().map(product_map)
    df.dropna(subset=['family'], inplace=True)

    df = pd.merge(df, warung_info, on='store_nbr', how='left')
    df.dropna(subset=['type'], inplace=True)
    
    agg_sales = df.groupby(['date', 'family', 'type'])['jumlah_terjual'].sum().reset_index()
    agg_sales.rename(columns={'jumlah_terjual': 'sales'}, inplace=True)
    return agg_sales

def run_prediction_pipeline(laporan_harian, warung_info):
    """Fungsi utama yang menjalankan pipeline prediksi per tipe."""
    
    # 1. Proses laporan harian yang masuk (diagregasi per Tipe Toko)
    sales_today_agg = map_and_agg_sales_by_type(laporan_harian, product_to_family_map, warung_info)
    
    # 2. Gabungkan data historis dengan data baru, lalu agregasi lagi untuk memastikan unik
    updated_data_raw = pd.concat([historical_data, sales_today_agg], ignore_index=True)
    grouping_cols = ['date', 'family', 'type']
    updated_data = updated_data_raw.groupby(grouping_cols)['sales'].sum().reset_index()

    all_predictions = []

    # 3. Lakukan Prediksi untuk Setiap Family
    for fam in tqdm(updated_data['family'].unique(), desc="Membuat Prediksi per Family"):
        if fam not in models_dict: continue
        
        model = models_dict[fam][0]
        pipeline = pipelines_dict[fam]
        
        # Buat TimeSeries dari data gabungan, digrupkan per 'type'
        target_series = TimeSeries.from_group_dataframe(
            updated_data[updated_data['family'] == fam],
            time_col='date', value_cols='sales',
            group_cols='type',
            freq='D', fill_missing_dates=True, fillna_value=0
        )
        
        series_transformed = pipeline.transform(target_series)
        pred_transformed = model.predict(n=1, series=series_transformed)
        pred_original = pipeline.inverse_transform(pred_transformed)
        pred_clipped = [p.map(lambda arr: np.clip(arr, a_min=0., a_max=None)) for p in pred_original]
        
        # Format output
        for ts in pred_clipped:
            tipe_toko = ts.static_covariates['type'].values[0]
            pred_value = ts.first_value()
            all_predictions.append({
                'date': ts.start_time().strftime('%Y-%m-%d'),
                'family': fam,
                'type': tipe_toko,
                'predicted_sales': round(pred_value, 2)
            })

    return pd.DataFrame(all_predictions)

try:
        historical_data_raw = pd.read_csv("dataset_fix.csv")
        historical_data_raw['date'] = pd.to_datetime(historical_data_raw['date'])
        # Pilih hanya kolom yang relevan
        historical_data = historical_data_raw[['date', 'family', 'type', 'sales']]
        print("✅ Data historis 'dataset_fix.csv' berhasil dimuat.")
except FileNotFoundError:
        print("\nPERINGATAN: File 'dataset_fix.csv' tidak ditemukan. Menggunakan data historis dummy.")
        # Jika file tidak ada, buat data historis dummy
        historical_dates = pd.to_datetime(pd.date_range(end=datetime.now().date() - timedelta(days=1), periods=30))
        historical_data = pd.DataFrame({
            'date': np.repeat(historical_dates, 4), 'family': ['BEVERAGES', 'GROCERY I'] * 60,
            'type': ['C', 'D', 'C', 'D'] * 30, 'sales': np.random.randint(50, 200, 120)
        })