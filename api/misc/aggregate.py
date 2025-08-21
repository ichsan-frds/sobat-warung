from datetime import datetime, timedelta

class Aggregate():
    def get_stock_by_phone_pipeline(phone_number: str):
        return [
            # 1. Cari owner by phone_number
            {"$match": {"phone_number": phone_number}},
            
            # 2. Join ke warung
            {"$lookup": {
                "from": "warung",
                "localField": "_id",
                "foreignField": "owner_id",
                "as": "warung_data"
            }},
            {"$unwind": "$warung_data"},
            
            # 3. Join ke stock
            {"$lookup": {
                "from": "stock",
                "localField": "warung_data._id",
                "foreignField": "warung_id",
                "as": "stock_data"
            }},
            {"$unwind": "$stock_data"},
            
            # 4. Join ke product
            {"$lookup": {
                "from": "product",
                "localField": "stock_data.product_id",
                "foreignField": "_id",
                "as": "product_data"
            }},
            {"$unwind": "$product_data"},
            
            # 5. Sort berdasarkan product_name ascending (A-Z)
            {"$sort": {"product_data.product_name": 1}},
            
            # 6. Pilih field
            {"$project": {
                "_id": 0,
                "product_name": "$product_data.product_name",
                "stock_count": "$stock_data.stock_count",
                "price": "$stock_data.price",
                "last_transaction": "$stock_data.last_transaction"
            }}
        ]
    
    def get_forecasted_products_group_by_kecamatan_pipeline(
        min_stores=3,          # Threshold jumlah toko minimal
        min_units_per_store=5, # Threshold kebutuhan minimal per toko
        dominance_gap_pct=0.1  # Selisih minimal dominasi produk
    ):
        today = datetime.now().date()
        normalized_today = datetime.combine(today, datetime.min.time())

        return [
            # 1. Filter forecast hari ini
            {
                "$match": {
                    "date": normalized_today
                }
            },

            # 2. Join forecast + warung
            {
                "$lookup": {
                    "from": "warung",
                    "localField": "warung_id",
                    "foreignField": "_id",
                    "as": "warung_info"
                }
            },
            {"$unwind": "$warung_info"},

            # 3. Filter toko dengan kebutuhan >= min_units_per_store
            {
                "$match": {
                    "predicted_sell": {"$gte": min_units_per_store}
                }
            },

            # 4. Join product buat ambil nama
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "product_info"
                }
            },
            {"$unwind": "$product_info"},

            # 5. Group by kecamatan + product_id
            {
                "$group": {
                    "_id": {
                        "kecamatan": "$warung_info.kecamatan",
                        "product_id": "$product_id"
                    },
                    "product_name": {"$first": "$product_info.product_name"},
                    "total_units": {"$sum": "$predicted_sell"},
                    "store_count": {"$addToSet": "$warung_id"},
                    "stores": {
                        "$push": {
                            "warung_id": "$warung_id",
                            "owner_id": "$warung_info.owner_id",
                            "predicted_sell": "$predicted_sell"
                        }
                    }
                }
            },

            # 6. Hitung jumlah toko
            {
                "$addFields": {
                    "store_count": {"$size": "$store_count"}
                }
            },

            # 7. Filter jumlah toko >= min_stores
            {
                "$match": {
                    "store_count": {"$gte": min_stores}
                }
            },

            # 8. Group lagi by kecamatan → list produk diurutkan total_units desc
            {
                "$group": {
                    "_id": "$_id.kecamatan",
                    "products": {
                        "$push": {
                            "product_id": "$_id.product_id",
                            "product_name": "$product_name",
                            "total_units": "$total_units",
                            "store_count": "$store_count",
                            "stores": "$stores"
                        }
                    }
                }
            },
            {
                "$project": {
                    "products": {
                        "$sortArray": {
                            "input": "$products",
                            "sortBy": {"total_units": -1}
                        }
                    }
                }
            },

            # 9. Ambil produk top & runner-up untuk cek dominasi
            {
                "$project": {
                    "top_product": {"$arrayElemAt": ["$products", 0]},
                    "runner_up": {"$arrayElemAt": ["$products", 1]}
                }
            },

            # 10. Filter dominasi
            {
                "$match": {
                    "$expr": {
                        "$or": [
                            {"$eq": ["$runner_up", None]},
                            {
                                "$gte": [
                                    "$top_product.total_units",
                                    {
                                        "$multiply": [
                                            "$runner_up.total_units",
                                            1 + dominance_gap_pct
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        ]
    
    def get_transactions_and_product(warung_id, target_date):
        return [
            {
            "$match": {
                "warung_id": warung_id,
                "date": target_date
            }
            },
            {
                "$lookup": {
                    "from": "product",               # Nama koleksi yang mau di-join
                    "localField": "product_id",      # Field di transaction
                    "foreignField": "_id",           # Field di product
                    "as": "product_info"             # Hasil join disimpan di field ini
                }
            },
            {
                "$unwind": {
                    "path": "$product_info",
                    # Kalau produk nggak ketemu, tetap simpan transaksi
                    "preserveNullAndEmptyArrays": True
                }
            }
        ]
    
    def get_days_left_by_warung_pipeline(warung_id):
        return [
            {
                "$match": {
                    "warung_id": warung_id
                }
            },
            {
                "$project": {
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$date"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$date"
                }
            },
            {
                "$count": "unique_days"
            }
        ]