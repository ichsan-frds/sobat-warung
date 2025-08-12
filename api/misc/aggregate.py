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
                "price": "$stock_data.price"
            }}
        ]